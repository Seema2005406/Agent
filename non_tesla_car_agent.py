import asyncio
import random
from langchain.llms import Ollama
from uagents import Agent, Context, Model

# Replace with Charging Agent's Address
RECIPIENT_ADDRESS = "agent1qdyx3r7a032luj5d8jmkmr228amdlrcwemrtr0cmv096yurky3tpvt06d0a"

class Message(Model):
    message: str

# Initialize Ollama with LLaMA 3 23B model
llm = Ollama(model="llama3.2:3b")

car1_agent = Agent(
    name="Car1Agent",
    port=8002,
    seed="car1_secret_phrase",
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Initial battery SOC (State of Charge) - Randomized for simulation
battery_soc = random.randint(40, 100)  # Starts between 40% and 100%
request_sent = False  # Flag to prevent multiple requests
monitoring_active = True  # Flag to control battery monitoring

async def monitor_battery(ctx: Context):
    """Continuously monitors the battery SOC and requests charging when needed."""
    global battery_soc, request_sent, monitoring_active

    while monitoring_active:  # Run only while monitoring is active
        await asyncio.sleep(5)  # Simulate battery draining every 5 seconds
        battery_soc -= random.randint(2, 5)  # Decrease SOC by 2-5% per cycle

        ctx.logger.info(f"🔋 Battery SOC: {battery_soc}%")

        if battery_soc <= 30 and not request_sent:
            ctx.logger.warning("⚠️ Battery low! Requesting a charging spot...")
            await request_charging(ctx)
            request_sent = True  # Prevent duplicate requests
            monitoring_active = False  # Stop battery monitoring after requesting charging

async def request_charging(ctx: Context):
    """Sends a charging request when the battery is low."""
    question = f"I am a Mercedes car. My battery is at {battery_soc}%. I need a charging spot immediately!"
    ctx.logger.info(f"🚀 Sending Message: {question}")
    await ctx.send(RECIPIENT_ADDRESS, Message(message=question))

@car1_agent.on_event('startup')
async def startup_event(ctx: Context):
    """Starts battery monitoring when the agent starts."""
    ctx.logger.info("🚗 Car Agent is online. Monitoring battery SOC...")
    asyncio.create_task(monitor_battery(ctx))

@car1_agent.on_message(model=Message)
async def handle_response(ctx: Context, sender: str, msg: Message):
    """Handles incoming messages from the Charge Agent."""
    global monitoring_active

    ctx.logger.info(f"📩 Received Message from {sender}: {msg.message}")

    # If the response confirms a charging spot was allocated, stop battery monitoring
    if "allocated spot" in msg.message:
        ctx.logger.info("✅ Charging spot received. Stopping battery monitoring.")
        monitoring_active = False  # Stop the battery monitoring loop

    # Generate an AI-enhanced response
    prompt = f"Charge agent response: '{msg.message}'\n Imagine You are car agent who requested spot and respond only using 5 words maximum "
    ai_response = llm.invoke(prompt)
    await ctx.send(RECIPIENT_ADDRESS, Message(message=ai_response))
   # ctx.logger.info(f"📤 AI Response: {ai_response}")

if __name__ == "__main__":
    car1_agent.run()
