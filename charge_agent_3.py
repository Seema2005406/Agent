from langchain.llms import Ollama
from uagents import Agent, Context, Model


# Initialize Ollama with LLaMA 3 23B model
llm = Ollama(model="llama3.2:3b")

# Charging spots database
charging_spots = [
    {"id": 1, "available": True, "supported_cars": "Non-Tesla"},
    {"id": 2, "available": True, "supported_cars": "Tesla"},
    {"id": 3, "available": True, "supported_cars": "Tesla"},
]

class Message(Model):
    message: str

charge_agent = Agent(
    name="ChargeAgent3",
    port=8005,
    seed="charge_secret_phrase3",
    endpoint=["http://127.0.0.1:8005/submit"],
)

def allocate_spot(car):
    """Finds an available spot and marks it as occupied."""
    if(car.lower() == "tesla"):
        for spot in charging_spots:
            if spot["available"] == True and spot["supported_cars"].lower() == "tesla":
                spot["available"] = False  # Mark as occupied
                return spot["id"]
    else:
        for spot in charging_spots:
            if spot["available"] == True and spot["supported_cars"].lower() != "tesla":
                spot["available"] = False  # Mark as occupied
                return spot["id"]
    return None  # No available spots

@charge_agent.on_message(model=Message)
async def handle_response(ctx: Context, sender: str, msg: Message):
    """Handles incoming messages and allocates a spot without checking for duplicates."""

    request_text = msg.message.lower()

    if "tesla" in request_text:
        spot_id = allocate_spot("tesla")
        if spot_id:
            response = f"✅ Charging spot {spot_id} allocated successfully."
            # ctx.logger.info(f"Allocated charging spot {spot_id} to car {sender}.")
            prompt = f"User request: '{request_text}'\nSystem decision: '{response}'\n Imagine You are charge agent and respond only about spot allocation or not only using 5 words maximum."
            ai_response = llm.invoke(prompt)
            await ctx.send(sender, Message(message=ai_response))
        else:
            response = "❌ Sorry, No charging spots available at the moment. Please try again later."
            # ctx.logger.info("No charging spots available.")
            # prompt = f"User request: '{request_text}'\nSystem decision: '{response}'\n Imagine You are charge agent and respond only about spot allocation or not only using 5 words maximum."
            # ai_response = llm.invoke(prompt)
            # await ctx.send(sender, Message(message=ai_response))
            await ctx.send(sender, Message(message=response))
    elif "mercedes" in request_text:
        spot_id = allocate_spot("mercedes")
        if spot_id:
            response = f"✅ Charging spot {spot_id} allocated successfully."
            # ctx.logger.info(f"Allocated charging spot {spot_id} to car {sender}.")
            prompt = f"User request: '{request_text}'\nSystem decision: '{response}'\n Imagine You are charge agent and respond only about spot allocation or not only using 5 words maximum."
            ai_response = llm.invoke(prompt)
            await ctx.send(sender, Message(message=ai_response))
        else:
            response = "❌ Sorry, No charging spots available at the moment. Please try again later."
            # ctx.logger.info("No charging spots available.")
            # prompt = f"User request: '{request_text}'\nSystem decision: '{response}'\n Imagine You are charge agent and respond only about spot allocation or not only using 5 words maximum."
            # ai_response = llm.invoke(prompt)
            # await ctx.send(sender, Message(message=ai_response))
            await ctx.send(sender, Message(message=response))

if __name__ == "__main__":
    # Start agent in a separate thread
    charge_agent.run()
