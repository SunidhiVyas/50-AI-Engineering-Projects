from __future__ import annotations

import argparse
import asyncio
import json
import os
from decimal import Decimal

import httpx
from agno.agent import Agent
from agno.models.ollama import Ollama
from eth_account import Account
from x402 import x402Client
from x402.http.clients.httpx import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact import ExactEvmScheme


USDC_DECIMALS = 6

SELLER = os.environ.get(
    "SELLER_URL",
    "http://localhost:4021"
)


def build_paying_client(
    private_key: str,
    max_price_usdc: Decimal
):
    """Create an x402 client that can automatically pay 402 challenges."""

    signer = EthAccountSigner(
        Account.from_key(private_key)
    )

    client = x402Client()

    max_atomic = int(
        max_price_usdc * (10 ** USDC_DECIMALS)
    )

    def budget_cap(version, accepts):

        allowed = [
            payment
            for payment in accepts
            if int(
                getattr(payment, "amount", 0)
                or getattr(payment, "max_amount_required", 0)
                or 0
            ) <= max_atomic
        ]

        if not allowed:
            raise ValueError(
                f"Payment exceeds ${max_price_usdc} limit."
            )

        return allowed

    client.register_policy(budget_cap)

    client.register(
        "eip155:*",
        ExactEvmScheme(signer)
    )

    return x402HttpxClient(
        client,
        follow_redirects=True,
        timeout=60.0
    )


async def paid_fetch(
    url: str,
    private_key: str,
    max_price_usdc: Decimal
):

    async with build_paying_client(
        private_key,
        max_price_usdc
    ) as client:

        response = await client.get(url)

        return response.status_code, response.text


def inspect_paid_api(url: str):

    """Check an x402 endpoint without making a payment."""

    response = httpx.get(
        url,
        timeout=30
    )

    print("\n===== x402 PAYMENT DEMO =====")
    print(f"URL: {url}")
    print(f"HTTP Status: {response.status_code}")

    if response.status_code == 402:

        payment_header = response.headers.get(
            "payment-required"
        )

        print("Payment Required: YES")
        print(
            "The API returned an x402 payment challenge."
        )

        if payment_header:
            print(
                "Payment challenge received successfully."
            )

        print(
            "\nNo wallet configured, so no payment was made."
        )

    elif response.status_code == 200:

        print("Payment Required: NO")
        print("The endpoint returned data.")

    else:

        print(
            f"Request returned HTTP {response.status_code}"
        )

    print("============================\n")


def run_agent(question: str):

    agent = Agent(
        name="X402 Paying Agent",
        model=Ollama(
            id="qwen2.5:0.5b"
        ),
        instructions=[
            "You are an AI agent that understands x402 paid APIs.",
            "Explain the x402 payment flow clearly.",
            "Do not invent payment results.",
            "Explain when an API requires HTTP 402 payment.",
            "Keep responses concise."
        ],
        markdown=True
    )

    response = agent.run(
        f"""
User question:

{question}

Explain how this question relates to the x402
payment API demonstrated by this project.
"""
    )

    print(response.content)


def main():

    parser = argparse.ArgumentParser(
        description="AI agent demonstrating x402 micropayments"
    )

    parser.add_argument(
        "question",
        nargs="?",
        help="Question for the AI agent"
    )

    parser.add_argument(
        "--direct",
        metavar="URL",
        help="Inspect an x402 API without making a payment"
    )

    args = parser.parse_args()

    if args.direct:

        inspect_paid_api(args.direct)

        return

    if not args.question:

        parser.error(
            "Provide a question or use --direct <URL>"
        )

    run_agent(args.question)


if __name__ == "__main__":
    main()