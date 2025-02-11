import asyncio
import random
from langchain.llms import Ollama
from uagents import Agent, Context, Model

# Replace with Charging Agent's Address
RECIPIENT_ADDRESS = [
    "agent1qwk300m6eswak0n9mnqmf8rrd8qdddldxl4jqljc4v3nc4kmxrq87jqcadw",
    "agent1q0qxgydn4szvweyh2kvetwmutptjg6dnrs5rvd7dsdnedel2f8xx6nql4ur",
    "agent1qw4kuszaufr2qcspv95xgvnx4vsyqaht737u7unmr56p7ehe2f8csau43xl"
]

address_counter = 0

class Message(Model):
    message: str

# Initialize Ollama with LLaMA 3 23B model
llm = Ollama(model="llama3.2:3b")

car2_agent = Agent(
    name="Car2Agent",
    port=8001,
    seed="car2_secret_phrase",
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Initial battery SOC (State of Charge) - Randomized for simulation
battery_soc = random.randint(40, 50)  # Starts between 40% and 50%
request_sent = False  # Flag to prevent multiple requests
monitoring_active = True  # Flag to control battery monitoring

async def get_user_confirmation(prompt: str):
    """Asks for user input asynchronously to avoid blocking."""
    user_input = await asyncio.to_thread(input, prompt + " (yes/no): ")
    return user_input.lower().strip()

async def monitor_battery(ctx: Context):
    """Continuously monitors the battery SOC and requests charging when needed."""
    global battery_soc, request_sent, monitoring_active

    while monitoring_active:  # Run only while monitoring is active
        await asyncio.sleep(5)  # Simulate battery draining every 5 seconds
        battery_soc -= random.randint(2, 5)  # Decrease SOC by 2-5% per cycle

        ctx.logger.info(f"🔋 Battery SOC: {battery_soc}%")

        if battery_soc <= 30 and not request_sent:
            ctx.logger.warning("⚠️ Battery low! Asking user for charging request...")

            # Ask the user for confirmation before requesting charging
            user_input = await get_user_confirmation("🔋 Battery low! Request a charging spot?")

            if user_input == "yes":
                await request_charging(ctx)
                request_sent = True  # Prevent duplicate requests
                monitoring_active = False  # Stop battery monitoring after requesting charging
            else:
                ctx.logger.info("🚗 User declined charging request. Continuing to monitor battery.")

async def request_charging(ctx: Context):
    """Sends a charging request when the battery is low."""
    global address_counter
    question = f"I am a Tesla car. My battery is at {battery_soc}%. I need a charging spot immediately!"
    ctx.logger.info(f"🚀 Sending Message: {question}")
    await ctx.send(RECIPIENT_ADDRESS[address_counter], Message(message=question))

@car2_agent.on_event('startup')
async def startup_event(ctx: Context):
    """Starts battery monitoring when the agent starts."""
    ctx.logger.info("🚗 Car Agent B is online. Monitoring battery SOC...")
    asyncio.create_task(monitor_battery(ctx))

@car2_agent.on_message(model=Message)
async def handle_response(ctx: Context, sender: str, msg: Message):
    """Handles incoming messages from the Charge Agent."""
    global monitoring_active
    global address_counter

    ctx.logger.info(f"📩 Received Message from {sender}: {msg.message}")

    # If the response confirms a charging spot was allocated, ask user for confirmation
    if "Sorry" not in msg.message:
        ctx.logger.info("✅ Charging spot received. Asking user for confirmation...")

        # Ask user if they want to proceed with the charging spot
        user_input = await get_user_confirmation(f"✅ Charging spot received: {msg.message}. Shall we proceed?")

        if user_input == "yes":
            ctx.logger.info("⚡ Proceeding with charging process...")
            monitoring_active = False  # Stop battery monitoring after charging confirmation
        else:
            ctx.logger.info("❌ User declined the charging spot.")
    else:
        if address_counter < len(RECIPIENT_ADDRESS) - 1:  # Try the next charging agent
            address_counter += 1
            await request_charging(ctx)

if __name__ == "__main__":
    car2_agent.run()

