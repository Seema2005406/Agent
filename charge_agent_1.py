from langchain.llms import Ollama
from uagents import Agent, Context, Model


# Initialize Ollama with LLaMA 3 23B model
llm = Ollama(model="llama3.2:3b")

# Charging spots database
charging_spots = [
    {"id": 1, "available": True, "supported_cars": "Non-Tesla"},
    {"id": 2, "available": True, "supported_cars": "Non-Tesla"},
    {"id": 3, "available": True, "supported_cars": "Non-Tesla"},
]

class Message(Model):
    message: str

charge_agent = Agent(
    name="ChargeAgent1",
    port=8003,
    seed="charge_secret_phrase1",
    endpoint=["http://127.0.0.1:8003/submit"],
)

def allocate_spot():
    """Finds an available spot and marks it as occupied."""
    for spot in charging_spots:
        if spot["available"]:
            spot["available"] = False  # Mark as occupied
            return spot["id"]
    return None  # No available spots

@charge_agent.on_message(model=Message)
async def handle_response(ctx: Context, sender: str, msg: Message):
    """Handles incoming messages and allocates a spot without checking for duplicates."""
    ctx.logger.info(f"📩 Received Message from {sender}: {msg.message}")
    request_text = msg.message.lower()

    # Tesla cars are not supported
    if "tesla" in request_text:
        response = "❌ Sorry, Tesla vehicles are not supported at this charging station."
        await ctx.send(sender, Message(message=response))
        ctx.logger.info(f"Rejected car {sender}: {response}")
    else:
        spot_id = allocate_spot()
        if spot_id:
            response = f"✅ Charging spot {spot_id} allocated successfully."
            # ctx.logger.info(f"Allocated charging spot {spot_id} to car {sender}.")
            prompt = f"User request: '{request_text}'\nSystem decision: '{response}'\n Imagine You are charge agent and respond only about spot allocation or not only using 5 words maximum."
            ai_response = llm.invoke(prompt)
            await ctx.send(sender, Message(message=ai_response))
            ctx.logger.info(f"📩 Send Message to {sender}: {ai_response}")
        else:
            response = "❌ Sorry, No charging spots available at the moment. Please try again later."
            # ctx.logger.info("No charging spots available.")
            # prompt = f"User request: '{request_text}'\nSystem decision: '{response}'\n Imagine You are charge agent and respond only about spot allocation or not only using 5 words maximum."
            # ai_response = llm.invoke(prompt)
            # await ctx.send(sender, Message(message=ai_response))
            await ctx.send(sender, Message(message=response))
            ctx.logger.info(f"📩 Send Message to {sender}: {response}")


if __name__ == "__main__":
    # Start agent in a separate thread
    charge_agent.run()
