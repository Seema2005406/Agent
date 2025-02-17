import asyncio
from kuksa_client.grpc import VSSClient
from uagents import Agent, Context, Model
from langchain.llms import Ollama

# Replace with Charging Agent's Address
RECIPIENT_ADDRESS = [
    "agent1qwk300m6eswak0n9mnqmf8rrd8qdddldxl4jqljc4v3nc4kmxrq87jqcadw",
    "agent1q0qxgydn4szvweyh2kvetwmutptjg6dnrs5rvd7dsdnedel2f8xx6nql4ur",
    "agent1qw4kuszaufr2qcspv95xgvnx4vsyqaht737u7unmr56p7ehe2f8csau43xl"
]

KUKSA_DATA_BROKER_IP = 'localhost'  # Replace with Kuksa server IP
KUKSA_DATA_BROKER_PORT = 55555  # Kuksa default port

address_counter = 0
battery_soc = 100  # Default value
request_sent = False
monitoring_active = True

class Message(Model):
    message: str

llm = Ollama(model="llama3.2:3b")

car2_agent = Agent(
    name="Car2Agent",
    port=8001,
    seed="car2_secret_phrase",
    endpoint=["http://127.0.0.1:8001/submit"],
)

async def get_user_confirmation(prompt: str):
    """Asks for user input asynchronously to avoid blocking."""
    user_input = await asyncio.to_thread(input, prompt + " (yes/no): ")
    return user_input.lower().strip()

async def monitor_battery(ctx: Context):
    """Monitors battery SOC from Kuksa and requests charging if needed."""
    global battery_soc, request_sent, monitoring_active

    with VSSClient(KUKSA_DATA_BROKER_IP, KUKSA_DATA_BROKER_PORT) as client:
        client.subscribe_current_values(['Vehicle.Powertrain.TractionBattery.StateOfCharge.Current'])
        ctx.logger.info("🔋 Subscribed to Kuksa battery SOC signal...")

        while monitoring_active:
            updates = client.get_current_values(['Vehicle.Batterysoc'])
            if 'Vehicle.Powertrain.TractionBattery.StateOfCharge.Current' in updates:
                battery_soc = updates['Vehicle.Powertrain.TractionBattery.StateOfCharge.Current'].value
                ctx.logger.info(f"🔋 Battery SOC: {battery_soc}%")

            if battery_soc <= 30 and not request_sent:
                ctx.logger.warning("⚠️ Battery low! Asking user for charging request...")
                user_input = await get_user_confirmation("🔋 Battery low! Request a charging spot?")
                if user_input == "yes":
                    await request_charging(ctx)
                    request_sent = True
                    monitoring_active = False
                else:
                    ctx.logger.info("🚗 User declined charging request. Continuing to monitor battery.")

            await asyncio.sleep(5)

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
    global monitoring_active, address_counter

    ctx.logger.info(f"📩 Received Message from {sender}: {msg.message}")

    if "Sorry" not in msg.message:
        ctx.logger.info("✅ Charging spot received. Asking user for confirmation...")
        user_input = await get_user_confirmation(f"✅ Charging spot received: {msg.message}. Shall we proceed?")
        if user_input == "yes":
            ctx.logger.info("⚡ Proceeding with charging process...")
            monitoring_active = False
        else:
            ctx.logger.info("❌ User declined the charging spot.")
    else:
        if address_counter < len(RECIPIENT_ADDRESS) - 1:
            address_counter += 1
            await request_charging(ctx)

if __name__ == "__main__":
    car2_agent.run()
