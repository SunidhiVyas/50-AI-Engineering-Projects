"""AI Fraud Investigation Agent — Surelock Homes Demo

Autonomous childcare provider anomaly investigation using public records,
property GIS data, optional Google Maps, and local Ollama.

Usage:
    streamlit run fraud_investigation_agent.py
"""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import requests
import streamlit as st
from agno.agent import Agent
from agno.models.ollama import Ollama
from bs4 import BeautifulSoup


# ── Constants ──────────────────────────────────────────────────────────────────

MAX_PROVIDER_CAP = 100
TOOL_TIMEOUT = 10
DCFS_TIMEOUT = 30
OLLAMA_MODEL = "qwen2.5:0.5b"


# ── Cook County Socrata endpoints ──────────────────────────────────────────────

_COOK_ADDR_URL = (
    "https://datacatalog.cookcountyil.gov/resource/3723-97qp.json"
)
_COOK_RES_URL = (
    "https://datacatalog.cookcountyil.gov/resource/x54s-btds.json"
)
_COOK_COMMERCIAL_URL = (
    "https://datacatalog.cookcountyil.gov/resource/csik-bsws.json"
)
_COOK_ASSESSED_URL = (
    "https://datacatalog.cookcountyil.gov/resource/uzyt-m557.json"
)

_IL_DCFS_URL = (
    "https://sunshine.dcfs.illinois.gov/"
    "Content/Licensing/Daycare/ProviderLookup.aspx"
)


# ── Google API helper ──────────────────────────────────────────────────────────

def _google_key() -> str:
    """Get Google Maps API key from Streamlit session state."""
    try:
        return st.session_state.get("google_maps_api_key", "")
    except Exception:
        return ""


# ── System Prompt ──────────────────────────────────────────────────────────────

_SYSTEM_PROMPT_TEMPLATE = """<identity>
The agent is Surelock Homes, an AI anomaly investigation agent powered
by a local Ollama model.

The current date is {today}.

Surelock Homes investigates public records and looks for inconsistencies
between licensing information and physical/property information.
</identity>

<mission>
Surelock Homes investigates subsidized childcare providers using
publicly available data.

The goal is to find facilities where physical evidence does not appear
to match licensing information and identify anomalies that require
further investigation.

Building capacity is an important signal. A building that appears too
small for its licensed capacity may indicate an inconsistency.

The agent must clearly distinguish between an anomaly and proven fraud.

CRITICAL SCOPE LIMITATION:
This system does NOT detect attendance fraud. Attendance fraud requires
non-public CCAP billing records and service authorizations.

Findings are investigation leads only.
</mission>

<investigative_approach>
The agent should investigate providers systematically while remaining
alert for unexpected patterns.

Important patterns include:

- Multiple providers sharing an address
- Owner or agent names appearing across providers
- Small buildings with unusually large licensed capacity
- Recently incorporated entities with unusual capacity
- Addresses that do not appear consistent with childcare use
- Providers with limited public presence
- Geographic clusters of unusual providers
- Active licenses with suspicious or incomplete public information

The agent should explain why a finding is unusual and what additional
information would be useful for verification.
</investigative_approach>

<domain_knowledge>
ILLINOIS DCFS CAPACITY RULE:

- Minimum 35 usable square feet per child indoors
- Usable space excludes hallways, bathrooms, kitchens, storage and staff areas
- Demo assumption: approximately 65% of total building square footage is usable
- Formula:

  max_children = (building_sqft × 0.65) ÷ 35

License types:

- Day Care Center: 8+
- Day Care Home: 4-12
- Group Day Care Home: up to 16
</domain_knowledge>

<guardrails>
LANGUAGE:

- Never state that a provider definitely committed fraud.
- Use phrases such as:
  "requires further investigation"
  "exhibits an anomaly"
  "raises a flag"
  "appears inconsistent"

- Never identify individuals as criminals.
- Present names only as public-record information when relevant.

METHODOLOGY:

- Show calculations.
- Name data sources.
- State assumptions.
- Acknowledge missing or potentially outdated information.

ETHICAL:

- Findings are investigation leads, not prosecution evidence.
- Consider innocent explanations.
- Public data may be incomplete.

SCOPE:

- Public data only.
- Visual analysis is probabilistic.
- Attendance fraud cannot be detected.
</guardrails>
"""


def _build_system_prompt() -> str:
    """Return system prompt with today's date."""
    return _SYSTEM_PROMPT_TEMPLATE.format(
        today=datetime.now().strftime("%Y-%m-%d")
    )


# ── Address helpers ────────────────────────────────────────────────────────────

_DIRECTION_RE = re.compile(
    r"^(N|S|E|W|NE|NW|SE|SW)\.?$",
    re.I,
)

_SUFFIX_MAP = {
    "STREET": "ST",
    "AVENUE": "AVE",
    "ROAD": "RD",
    "DRIVE": "DR",
    "BOULEVARD": "BLVD",
    "PLACE": "PL",
    "COURT": "CT",
    "LANE": "LN",
    "WAY": "WAY",
    "CIRCLE": "CIR",
    "TRAIL": "TRL",
    "PARKWAY": "PKWY",
}


def _parse_address(address: str) -> dict[str, str]:
    """Extract basic address components."""
    clean = address.split(",")[0].strip().upper()
    tokens = clean.split()

    if not tokens:
        return {}

    result: dict[str, str] = {}
    idx = 0

    if tokens[idx].isdigit() or re.match(r"^\d+\w*$", tokens[idx]):
        result["house"] = tokens[idx]
        idx += 1

    if idx < len(tokens) and _DIRECTION_RE.match(tokens[idx]):
        result["direction"] = tokens[idx].upper()
        idx += 1

    street_tokens = []

    while idx < len(tokens):
        token = tokens[idx]
        normalized = _SUFFIX_MAP.get(token)

        if normalized:
            result["suffix"] = normalized
            idx += 1
            break

        street_tokens.append(token)
        idx += 1

    result["street"] = " ".join(street_tokens)

    return result


# ── Tool 1: Search childcare providers ───────────────────────────────────────

def search_childcare_providers(
    zip_code: str,
    state: str = "IL",
) -> str:
    """Search for licensed childcare providers in an Illinois ZIP code."""

    if state.upper() != "IL":
        return json.dumps({
            "status": "error",
            "error": "Only Illinois (IL) is supported in this demo.",
        })

    if not re.match(r"^\d{5}$", str(zip_code).strip()):
        return json.dumps({
            "status": "error",
            "error": f"Invalid ZIP code '{zip_code}'.",
        })

    try:
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0"}

        page = session.get(
            _IL_DCFS_URL,
            headers=headers,
            timeout=DCFS_TIMEOUT,
        )
        page.raise_for_status()

        soup = BeautifulSoup(page.text, "html.parser")

        form_data: dict[str, str] = {}

        for element in soup.find_all("input"):
            name = element.get("name")

            if name:
                form_data[name] = element.get("value", "")

        form_data["__EVENTTARGET"] = (
            "ctl00$ContentPlaceHolderContent$ASPxSearch"
        )

        for key in list(form_data.keys()):
            if (
                key.endswith("ASPxSearch")
                and key.startswith("ctl00$ContentPlaceHolderContent$")
            ):
                form_data[key] = "Search"

        response = session.post(
            _IL_DCFS_URL,
            data=form_data,
            headers=headers,
            timeout=DCFS_TIMEOUT,
        )

        response.raise_for_status()

        providers = []

        for row in csv.reader(io.StringIO(response.text)):
            if len(row) < 17:
                continue

            if not re.match(r"^\d{6}$", str(row[0]).strip()):
                continue

            row_zip = str(row[5]).strip().split("-")[0][:5]
            target_zip = str(zip_code).strip()[:5]

            if row_zip != target_zip:
                continue

            try:
                capacity = int(
                    float(str(row[14]).strip() or "0")
                )
            except ValueError:
                capacity = 0

            providers.append({
                "name": str(row[1]).strip(),
                "address": str(row[2]).strip(),
                "city": str(row[3]).strip(),
                "zip": row_zip,
                "capacity": capacity,
                "license_type": str(row[7]).strip(),
                "status": str(row[16]).strip(),
                "license_number": str(row[0]).strip(),
                "state": "IL",
            })

        capped = providers[:MAX_PROVIDER_CAP]

        return json.dumps({
            "status": "ok",
            "zip_code": zip_code,
            "total_found": len(providers),
            "providers_returned": len(capped),
            "note": (
                f"Showing {len(capped)} of {len(providers)} providers."
                if len(providers) > MAX_PROVIDER_CAP
                else ""
            ),
            "providers": capped,
        })

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "error": str(exc),
        })


# ── Tool 2: Property data ─────────────────────────────────────────────────────

def get_property_data(
    address: str,
    county: str = "Cook",
    state: str = "IL",
) -> str:
    """Get property and building data from Cook County records."""

    if not address:
        return json.dumps({
            "status": "error",
            "error": "address is required",
        })

    try:
        parsed = _parse_address(address)

        if "house" not in parsed or "street" not in parsed:
            return json.dumps({
                "status": "error",
                "error": f"Could not parse address: {address}",
            })

        parts = [parsed["house"]]

        if parsed.get("direction"):
            parts.append(parsed["direction"])

        parts.append(parsed["street"])

        if parsed.get("suffix"):
            parts.append(parsed["suffix"])

        addr_prefix = " ".join(parts)
        safe_prefix = addr_prefix.replace("'", "''")

        pin: Optional[str] = None

        for query_pattern in [
            f"prop_address_full='{safe_prefix}'",
            f"starts_with(prop_address_full, '{safe_prefix}')",
        ]:
            params = {
                "$where": query_pattern,
                "$select": "pin",
                "$order": "year DESC",
                "$limit": "1",
            }

            response = requests.get(
                _COOK_ADDR_URL,
                params=params,
                timeout=TOOL_TIMEOUT,
            )

            response.raise_for_status()

            rows = response.json()

            if rows:
                pin = rows[0].get("pin")
                break

        if not pin:
            return json.dumps({
                "status": "not_found",
                "address": address,
                "building_sqft": 0.0,
                "county": county,
                "state": state,
                "error": "No parcel PIN found.",
            })

        response = requests.get(
            _COOK_RES_URL,
            params={
                "pin": pin,
                "$select": (
                    "char_bldg_sf,char_land_sf,"
                    "char_yrblt,class"
                ),
                "$order": "year DESC",
                "$limit": "1",
            },
            timeout=TOOL_TIMEOUT,
        )

        response.raise_for_status()

        rows = response.json()

        if rows and rows[0]:
            row = rows[0]
            sqft = float(row.get("char_bldg_sf") or 0)

            if sqft > 0:
                return json.dumps({
                    "status": "ok",
                    "address": address,
                    "building_sqft": sqft,
                    "lot_size": str(
                        int(float(row.get("char_land_sf") or 0))
                    ),
                    "zoning": "",
                    "property_class": row.get("class", ""),
                    "year_built": int(
                        float(row.get("char_yrblt") or 0)
                    ),
                    "county": "Cook",
                    "state": state,
                    "pin": pin,
                    "source": (
                        "Cook County Residential "
                        "Characteristics (Socrata)"
                    ),
                })

        dashed = (
            f"{pin[:2]}-{pin[2:4]}-{pin[4:7]}-"
            f"{pin[7:10]}-{pin[10:]}"
            if len(pin) == 14
            else pin
        )

        response = requests.get(
            _COOK_COMMERCIAL_URL,
            params={
                "keypin": dashed,
                "$select": (
                    "bldgsf,landsf,yearbuilt,"
                    "property_type_use"
                ),
                "$order": "year DESC",
                "$limit": "1",
            },
            timeout=TOOL_TIMEOUT,
        )

        response.raise_for_status()

        rows = response.json()

        if rows and rows[0]:
            row = rows[0]
            sqft = float(row.get("bldgsf") or 0)

            if sqft > 0:
                return json.dumps({
                    "status": "ok",
                    "address": address,
                    "building_sqft": sqft,
                    "lot_size": str(
                        int(float(row.get("landsf") or 0))
                    ),
                    "zoning": "",
                    "property_class": row.get(
                        "property_type_use",
                        "",
                    ),
                    "year_built": int(
                        float(row.get("yearbuilt") or 0)
                    ),
                    "county": "Cook",
                    "state": state,
                    "pin": pin,
                    "source": (
                        "Cook County Commercial "
                        "Valuation (Socrata)"
                    ),
                })

        return json.dumps({
            "status": "ok",
            "address": address,
            "building_sqft": 0.0,
            "lot_size": "",
            "zoning": "",
            "property_class": "",
            "year_built": 0,
            "county": "Cook",
            "state": state,
            "pin": pin,
            "source": "Cook County Assessed Values",
            "note": "No building square footage found.",
        })

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "address": address,
            "error": str(exc),
        })


# ── Tool 3: Capacity calculation ──────────────────────────────────────────────

_CAPACITY_REGS = {
    "IL": {
        "sqft_per_child": 35,
        "regulation": "IL DCFS Title 89, Part 407",
    },
    "MN": {
        "sqft_per_child": 35,
        "regulation": "MN Rules 9503.0155",
    },
}


def calculate_max_capacity(
    building_sqft: float,
    state: str = "IL",
    usable_ratio: float = 0.65,
) -> str:
    """Calculate maximum legal childcare capacity."""

    state_key = state.upper()
    reg = _CAPACITY_REGS.get(state_key)

    if not reg:
        return json.dumps({
            "status": "error",
            "error": f"State {state} is not supported.",
        })

    if not building_sqft or building_sqft <= 0:
        return json.dumps({
            "status": "error",
            "error": "building_sqft must be greater than 0.",
        })

    sqft_per_child = reg["sqft_per_child"]

    usable_sqft = (
        float(building_sqft) *
        float(usable_ratio)
    )

    max_legal = int(
        usable_sqft // sqft_per_child
    )

    return json.dumps({
        "status": "ok",
        "building_sqft": float(building_sqft),
        "usable_ratio": usable_ratio,
        "usable_sqft": round(usable_sqft, 1),
        "sqft_per_child_required": sqft_per_child,
        "max_legal_capacity": max_legal,
        "state": state_key,
        "regulation": reg["regulation"],
        "calculation": (
            f"{building_sqft} sqft × "
            f"{usable_ratio} usable ratio = "
            f"{usable_sqft:.0f} usable sqft ÷ "
            f"{sqft_per_child} sqft/child = "
            f"{max_legal} children max"
        ),
    })


# ── Tool 4: Geocoding ──────────────────────────────────────────────────────────

def geocode_address(address: str) -> str:
    """Convert an address to latitude and longitude."""

    if not address:
        return json.dumps({
            "status": "error",
            "error": "address is required",
        })

    api_key = _google_key()

    if not api_key:
        return json.dumps({
            "status": "no_key",
            "address": address,
            "note": "Google Maps API key not configured.",
        })

    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": address,
                "key": api_key,
            },
            timeout=TOOL_TIMEOUT,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("status") == "REQUEST_DENIED":
            return json.dumps({
                "status": "error",
                "error": payload.get(
                    "error_message",
                    "Request denied",
                ),
            })

        results = payload.get("results", [])

        if not results:
            return json.dumps({
                "status": "not_found",
                "address": address,
            })

        location = results[0]["geometry"]["location"]

        return json.dumps({
            "status": "ok",
            "address": address,
            "formatted_address": results[0].get(
                "formatted_address"
            ),
            "lat": location.get("lat"),
            "lng": location.get("lng"),
        })

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "address": address,
            "error": str(exc),
        })


# ── Tool 5: Street View ────────────────────────────────────────────────────────

def get_street_view(address: str) -> str:
    """Capture Google Street View images when an API key is available."""

    if not address:
        return json.dumps({
            "status": "error",
            "error": "address is required",
        })

    api_key = _google_key()

    if not api_key:
        return json.dumps({
            "status": "no_key",
            "address": address,
            "note": "Google Maps API key not configured.",
        })

    headings = [0, 90, 180, 270]
    images = []

    try:
        for heading in headings:
            params = {
                "location": address,
                "heading": heading,
                "size": "640x480",
                "key": api_key,
            }

            metadata_response = requests.get(
                "https://maps.googleapis.com/maps/api/streetview/metadata",
                params={
                    **params,
                    "return_error_codes": True,
                },
                timeout=TOOL_TIMEOUT,
            )

            metadata = metadata_response.json()

            if metadata.get("status") == "REQUEST_DENIED":
                return json.dumps({
                    "status": "error",
                    "error": metadata.get(
                        "error_message",
                        "Street View denied",
                    ),
                })

            if metadata.get("status") != "OK":
                continue

            image_response = requests.get(
                "https://maps.googleapis.com/maps/api/streetview",
                params=params,
                timeout=TOOL_TIMEOUT,
            )

            image_response.raise_for_status()

            images.append({
                "heading": heading,
                "capture_date": metadata.get(
                    "date",
                    "unknown",
                ),
                "image_bytes": image_response.content,
            })

        if not images:
            return json.dumps({
                "status": "no_imagery",
                "address": address,
                "note": "No Street View imagery available.",
            })

        cache = st.session_state.setdefault(
            "street_view_cache",
            {},
        )

        cache[address] = [
            {
                "heading": image["heading"],
                "capture_date": image["capture_date"],
                "image_bytes": image["image_bytes"],
            }
            for image in images
        ]

        return json.dumps({
            "status": "ok",
            "address": address,
            "images_captured": len(images),
            "capture_date": images[0].get(
                "capture_date",
                "unknown",
            ),
        })

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "address": address,
            "error": str(exc),
        })


# ── Tool 6: Google Places ──────────────────────────────────────────────────────

def get_places_info(
    address: str,
    name: str = "",
) -> str:
    """Get Google Places information for an address."""

    if not address:
        return json.dumps({
            "status": "error",
            "error": "address is required",
        })

    api_key = _google_key()

    if not api_key:
        return json.dumps({
            "status": "no_key",
            "address": address,
            "note": "Google Maps API key not configured.",
        })

    try:
        query_plan = []

        if name:
            query_plan.append(
                (f"{name.strip()} {address}", False)
            )
            query_plan.append(
                (name.strip(), False)
            )

        query_plan += [
            (f"childcare {address}", True),
            (f"day care {address}", True),
            (address, False),
        ]

        place_id: Optional[str] = None

        for query, require_childcare in query_plan:
            response = requests.get(
                "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                params={
                    "input": query,
                    "inputtype": "textquery",
                    "fields": "place_id,name,types",
                    "key": api_key,
                },
                timeout=TOOL_TIMEOUT,
            )

            response.raise_for_status()

            payload = response.json()

            for candidate in payload.get(
                "candidates",
                [],
            ):
                if require_childcare:
                    types_string = " ".join(
                        str(item)
                        for item in candidate.get(
                            "types",
                            [],
                        )
                    )

                    name_string = str(
                        candidate.get("name", "")
                    )

                    combined = (
                        types_string +
                        " " +
                        name_string
                    ).lower()

                    if not any(
                        term in combined
                        for term in (
                            "daycare",
                            "day care",
                            "child",
                            "preschool",
                            "school",
                        )
                    ):
                        continue

                place_id = candidate.get("place_id")

                if place_id:
                    break

            if place_id:
                break

        if not place_id:
            return json.dumps({
                "status": "no_place",
                "address": address,
                "note": "No Google Places listing found.",
            })

        detail_response = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": (
                    "name,business_status,rating,"
                    "user_ratings_total,types,reviews,"
                    "formatted_address"
                ),
                "key": api_key,
            },
            timeout=TOOL_TIMEOUT,
        )

        detail_response.raise_for_status()

        detail = detail_response.json().get(
            "result",
            {},
        )

        expected_house = re.search(
            r"\b(\d+)\b",
            address or "",
        )

        formatted = detail.get(
            "formatted_address",
            "",
        )

        if expected_house and formatted:
            if not re.search(
                rf"\b{re.escape(expected_house.group(1))}\b",
                formatted,
            ):
                return json.dumps({
                    "status": "address_mismatch",
                    "address": address,
                    "note": (
                        f"Place result address '{formatted}' "
                        "does not match expected street number."
                    ),
                })

        reviews = [
            {
                "author": review.get("author_name"),
                "rating": review.get("rating"),
                "text": review.get("text", "")[:200],
            }
            for review in detail.get(
                "reviews",
                [],
            )[:3]
        ]

        return json.dumps({
            "status": "ok",
            "address": address,
            "place_name": detail.get("name"),
            "formatted_address": formatted,
            "business_type": ", ".join(
                detail.get("types", [])
            ),
            "operating_status": detail.get(
                "business_status"
            ),
            "rating": detail.get("rating"),
            "review_count": detail.get(
                "user_ratings_total",
                0,
            ),
            "recent_reviews": reviews,
        })

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "address": address,
            "error": str(exc),
        })


# ── Tool 7: Business registration ─────────────────────────────────────────────

def check_business_registration(
    name: str,
    state: str = "IL",
) -> str:
    """Check Illinois business registration information."""

    if not name:
        return json.dumps({
            "status": "error",
            "error": "name is required",
        })

    state_key = state.upper()

    if state_key != "IL":
        return json.dumps({
            "status": "error",
            "error": "Only Illinois is supported.",
        })

    try:
        endpoint = (
            "https://www.cyberdriveillinois.com/"
            "corpservices/api/entitysearch?"
            + urlencode({
                "searchstring": name.strip().lower()
            })
        )

        response = requests.get(
            endpoint,
            timeout=TOOL_TIMEOUT,
        )

        if response.status_code == 403:
            return json.dumps({
                "status": "blocked",
                "query": name,
                "state": state_key,
                "note": (
                    "Illinois SOS API returned 403. "
                    "Manual lookup may be required."
                ),
            })

        if 200 <= response.status_code < 400:
            data = (
                response.json()
                if response.headers.get(
                    "content-type",
                    "",
                ).startswith("application/json")
                else {}
            )

            if data:
                return json.dumps({
                    "status": "ok",
                    "query": name,
                    "state": state_key,
                    "results": data,
                })

            return json.dumps({
                "status": "reachable_no_data",
                "query": name,
                "state": state_key,
                "note": "Endpoint returned no parseable data.",
            })

        return json.dumps({
            "status": "error",
            "query": name,
            "state": state_key,
            "error": (
                f"IL SOS returned HTTP "
                f"{response.status_code}"
            ),
        })

    except requests.exceptions.ConnectionError:
        return json.dumps({
            "status": "unavailable",
            "query": name,
            "state": state_key,
            "note": "IL SOS API unreachable.",
        })

    except Exception as exc:
        return json.dumps({
            "status": "error",
            "query": name,
            "state": state_key,
            "error": str(exc),
        })


# ── Streamlit App ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Surelock Homes — AI Fraud Investigation Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 AI Fraud Investigation Agent")

st.caption(
    "Local AI investigation of childcare licensing anomalies "
    "using public records, Cook County property data, "
    "and optional Google Maps."
)


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Configuration")

    st.success(
        f"Local model: {OLLAMA_MODEL}"
    )

    google_key = st.text_input(
        "Google Maps API Key",
        type="password",
        help=(
            "Optional. Enables Geocoding, Places, "
            "and Street View analysis."
        ),
    )

    _COOK_COUNTY_ZIPS = [
        "60623",
        "60629",
        "60644",
        "60621",
        "60628",
        "60619",
        "60636",
        "60612",
        "60620",
        "60624",
    ]

    zip_code = st.selectbox(
        "ZIP Code (Cook County, IL)",
        options=_COOK_COUNTY_ZIPS,
        index=_COOK_COUNTY_ZIPS.index("60623"),
        help="Property data is available for Cook County ZIPs.",
    )

    investigate_btn = st.button(
        "🔍 Start Investigation",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    st.markdown(
        "**About:** Surelock Homes is a local AI "
        "anomaly-investigation demo for subsidized childcare."
    )

    st.markdown(
        "**Scope:** Illinois only. Uses public data. "
        "Findings are investigation leads, not accusations."
    )


# ── Main area ──────────────────────────────────────────────────────────────────

if not investigate_btn:

    st.info(
        "Select a Cook County ZIP code and click "
        "**Start Investigation**."
    )

    with st.expander("How it works"):

        st.markdown(
            """
### Investigation tools

| Tool | Purpose |
|---|---|
| `search_childcare_providers` | Illinois DCFS licensing records |
| `get_property_data` | Cook County property data |
| `calculate_max_capacity` | Building capacity calculation |
| `geocode_address` | Optional Google geocoding |
| `get_street_view` | Optional Street View evidence |
| `get_places_info` | Optional Google Places data |
| `check_business_registration` | Illinois business registration |

### What it looks for

- Licensed capacity that appears too high for building size
- Address inconsistencies
- Multiple providers sharing an address
- Missing public business presence
- Repeated names or addresses
- Geographic patterns
- Other public-data anomalies

### Important limitation

This project does **not** detect attendance fraud or billing fraud
that requires non-public CCAP records.
"""
        )


elif investigate_btn:

    st.session_state["google_maps_api_key"] = (
        google_key or ""
    )

    query = (
        f"Investigate licensed childcare providers "
        f"in ZIP code {zip_code}, Illinois. "
        f"Start by finding providers. "
        f"For relevant providers, compare licensed capacity "
        f"with property building size and calculate the "
        f"estimated maximum capacity. "
        f"Use Google tools only if available. "
        f"Look for anomalies and explain the evidence. "
        f"Do not accuse anyone of fraud. "
        f"End with a concise summary of providers requiring "
        f"further investigation."
    )

    st.markdown(
        f"### Investigation: ZIP {zip_code}"
    )

    st.markdown(
        f"*Model: `{OLLAMA_MODEL}`*"
    )

    st.divider()

    try:

        agent = Agent(
            model=Ollama(
                id=OLLAMA_MODEL
            ),
            tools=[
                search_childcare_providers,
                get_property_data,
                calculate_max_capacity,
                geocode_address,
                get_street_view,
                get_places_info,
                check_business_registration,
            ],
            description=_build_system_prompt(),
            instructions=[
                f"Investigate providers returned for ZIP {zip_code}.",
                "Start with provider licensing information.",
                "For high-capacity providers, compare property size and licensed capacity.",
                "Use calculate_max_capacity when building square footage is available.",
                "Use Google tools only when a Google Maps key is available.",
                "Cross-reference business registrations when useful.",
                "Explain evidence and uncertainty clearly.",
                "Never state that a provider committed fraud.",
                "Use anomaly and requires-further-investigation language.",
                "End with flagged providers and important patterns.",
            ],
            markdown=True,
            compress_tool_results=True,
        )

    except Exception as exc:

        st.error(
            f"Failed to initialize local AI agent: {exc}"
        )

        st.stop()

    narration_area = st.empty()
    parts: list[str] = []

    try:

        with st.spinner(
            "Investigation in progress..."
        ):

            for chunk in agent.run(
                query,
                stream=True,
            ):

                content = getattr(
                    chunk,
                    "content",
                    None,
                )

                if content:

                    parts.append(content)

                    narration_area.markdown(
                        "".join(parts)
                    )

        st.success(
            "Investigation complete."
        )

        # ── Street View results ────────────────────────────────────────────────

        street_view_cache: dict = (
            st.session_state.get(
                "street_view_cache",
                {},
            )
        )

        if street_view_cache:

            st.markdown(
                "### Street View Images"
            )

            for address, frames in street_view_cache.items():

                st.markdown(
                    f"**{address}**"
                )

                columns = st.columns(
                    min(len(frames), 4)
                )

                for column, frame in zip(
                    columns,
                    frames,
                ):

                    column.image(
                        frame["image_bytes"],
                        caption=(
                            f"Heading {frame['heading']}° · "
                            f"{frame['capture_date']}"
                        ),
                        use_container_width=True,
                    )

            st.session_state.pop(
                "street_view_cache",
                None,
            )

    except Exception as exc:

        st.error(
            f"Investigation error: {exc}"
        )

        partial = "".join(parts)

        if partial:

            st.markdown(
                "**Partial results:**"
            )

            st.markdown(partial)