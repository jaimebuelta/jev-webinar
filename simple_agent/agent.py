import asyncio
from rich.console import Console
from rich.markdown import Markdown

from mcp import Client
from ollama import AsyncClient

from verify_movie import verify_movie as _verify_movie

MCP_URL = 'http://127.0.0.1:8000/mcp'


console = Console()

# MODEL = 'qwen3.8'     # bigger model, ~32GB RAM
# MODEL = 'qwen3.5:9b'  # smaller model, ~15GB RAM
MODEL = 'qwen3.5:4b'  # even smaller, ~4GB RAM


PROMPT = '''
Recommend me a scary movie from the 80s, checking
that is adequate for my taste.

You can try different years to find the right movie
as well as dig deeper into a particular year.
'''

messages = [{'role': 'user', 'content': PROMPT}]


def verify_movie(movie_info: dict):
    '''
    Validate a movie is adequate to my taste
    '''
    return _verify_movie(movie_info)


available_functions = {
  'verify_movie': verify_movie,
}


def mcp_to_ollama(tool):
    return {
        'type': 'function',
        'function': {
            'name': tool.name,
            'description': tool.description or '',
            'parameters': tool.input_schema,
        },
    }


separator = Markdown('---')


async def main():
    async with Client(MCP_URL) as mcp_client:
        mcp_tools = (await mcp_client.list_tools()).tools
        mcp_names = {t.name for t in mcp_tools}
        tools = [verify_movie] + [mcp_to_ollama(t) for t in mcp_tools]

        llm_client = AsyncClient()
        while True:

            response = await llm_client.chat(model=MODEL,
                                             messages=messages,
                                             think=True,
                                             tools=tools)
            # Track the context size
            size = round(response.prompt_eval_count / 1000., 3)
            console.print('Current context size: ', size, 'K tokens')

            messages.append(response.message)
            console.print(response.message.thinking, style='dim')
            md_content = Markdown(response.message.content)
            console.print(md_content)

            if not response.message.tool_calls:
                # end the loop when there are no more tool calls
                break
            else:
                for tc in response.message.tool_calls:
                    name, args = tc.function.name, tc.function.arguments
                    console.print(f"Calling {name} with arguments {args}", style='dim')
                    if name in mcp_names:
                        console.print("MCP Call", style='dim')
                        # Call the MCP server for this tool
                        res = await mcp_client.call_tool(name, args)
                        result = (res.structured_content
                                    or '\n'.join(c.text for c in res.content if c.type == 'text'))
                    elif name in available_functions:
                        result = available_functions[name](**args)
                    console.print(f"Result: {result}", style='dim')
                    # add the tool result to the messages
                    messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})

            # continue the loop with the updated messages
            console.print(separator)


# Run the agent
asyncio.run(main())
