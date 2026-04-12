from __future__ import annotations

from agent.graph import AutoStreamAgent


WELCOME = """
AutoStream Conversational AI Agent
Type 'exit' to quit.
""".strip()


def main() -> None:
    print(WELCOME)
    agent = AutoStreamAgent()

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Assistant: Goodbye!")
            break

        result = agent.chat(user_input)
        print(f"Assistant: {result['response']}")
        print(f"[intent={result['intent']}, lead_captured={result['lead_captured']}]")


if __name__ == "__main__":
    main()
