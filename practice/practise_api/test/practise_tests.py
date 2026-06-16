import pytest

@pytest.mark.asyncio
async def check_post(client):
    create=await client.post('/trades',json={
        "name":"Aniket",
    })  