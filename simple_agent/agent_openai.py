import asyncio
from rich.console import Console
from rich.markdown import Markdown

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStreamableHttp

from dotenv import load_dotenv

from verify_movie import verify_movie as _verify_movie

load_dotenv()

MCP_URL = 'http://127.0.0.1:8000/mcp'


console = Console()

# MODEL = 'gpt-6-sol'    # bigger model, most capable and expensive
# MODEL = 'gpt-6-terra'  # smaller model, balanced capability and cost
MODEL = 'gpt-6-luna'  # even smaller, fastest and cheapest


PROMPT = '''
Recommend me a scary movie from the 80s, checking
that is adequate for my taste.

You can try different years to find the right movie
as well as dig deeper into a particular year.
'''


# strict_mode is disabled as the strict JSON schema doesn't allow a free-form dict
@function_tool(strict_mode=False)
def verify_movie(movie_info: dict):
    '''
    Validate a movie is adequate to my taste
    '''
    console.print(f'verify_movie: {movie_info}', style='dim')
    return _verify_movie(movie_info)


async def main():
    async with MCPServerStreamableHttp(params={'url': MCP_URL}, name='movies') as mcp_server:
        agent = Agent(name='Movie recommender',
                      model=MODEL,
                      tools=[verify_movie],
                      mcp_servers=[mcp_server])

        # The SDK runs the loop calling the tools until there are no more tool calls
        result = await Runner.run(agent, input=PROMPT, max_turns=50)
        console.print(Markdown(result.final_output))


# Run the agent
asyncio.run(main())
