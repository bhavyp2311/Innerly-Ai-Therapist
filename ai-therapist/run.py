from engine import respond

print("Therapist AI (type 'exit' to quit)\n")

while True:
    user = input("You: ").strip()
    if user.lower() in ["exit", "quit"]:
        break

    reply = respond(user)
    print("AI:", reply, "\n")