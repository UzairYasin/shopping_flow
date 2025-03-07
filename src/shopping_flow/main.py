import chainlit as cl
import asyncio
from crewai.flow import Flow, start
from shopping_flow.crews.shopping_crew.shopping_crew import ShoppingCrew

class ShoppingFlow(Flow):
    @start()
    def find_best_products(self, product_prompt):
        # This is a synchronous method
        result = ShoppingCrew().crew().kickoff(inputs={"product": product_prompt})
        return result

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("flow", ShoppingFlow())

@cl.on_message
async def on_message(message: cl.Message):
    flow = cl.user_session.get("flow")
    
    # Show thinking indicator while processing
    with cl.Step(name="Finding Best Products") as step:
        step.input = message.content
        
        # Create a temporary thinking message
        thinking_msg = cl.Message(content="Processing your request...")
        await thinking_msg.send()
        
        # Run the synchronous CrewAI operation in a separate thread to not block the async event loop
        # This is a common pattern for running sync code in async contexts
        result = await asyncio.to_thread(flow.find_best_products, message.content)
        
        # Update the step with the result
        step.output = result
        
        # Remove the thinking message
        await thinking_msg.update()
        await thinking_msg.remove()
    
    # Send final result to user
    await cl.Message(content=result).send()

def plot():
    poem_flow = ShoppingFlow()
    poem_flow.plot()

# The following is only used when running the script directly
# Chainlit will use its own entry point
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "plot":
        plot()
    else:
        # This won't be used when running with chainlit
        print("To use the UI, run with: chainlit run main.py")