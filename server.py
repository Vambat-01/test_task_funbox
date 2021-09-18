from fastapi import FastAPI, Query, Request
from uvicorn import Config, Server
from models import DomainNames, LinkRequest
import redis
import asyncio
import datetime
import uuid
from models import DomainsResponse
from models import ValidationException
from fastapi.responses import JSONResponse
import typer


def main(server_host: str, server_port: int, redis_host: str, redis_port: int):

    async def do_main():
        app = FastAPI()

        with redis.Redis(host=redis_host, port=redis_port) as server_redis:
            @app.exception_handler(ValidationException)
            async def on_validation_exception(request: Request, exception: ValidationException):
                return JSONResponse(status_code=400, content={"status": exception.name})

            @app.post("/visited_links")
            async def visited_links(req: LinkRequest):
                id = str(uuid.uuid4())
                domain_names = req.get_domain_names(req.links, id)
                time = get_unix_time()
                server_redis.zadd("links", {domain_names.json(): time})
                return {"status": "ok"}

            @app.get("/visited_domains")
            async def visited_domains(to: float, from_: float = Query(..., alias="from")):
                bytes_domain_names = server_redis.zrangebyscore("links", from_, to)
                domain_names = [DomainNames.parse_bytes(b) for b in bytes_domain_names]
                return DomainsResponse.from_domains(domain_names)

        config = Config(app=app, host=server_host, port=server_port)
        server = Server(config)
        await server.serve()

    asyncio.run(do_main())


def get_unix_time() -> float:
    """
        Возвращает текущее время в unix формате
    :return: unix время
    """
    time_now = datetime.datetime.now()
    return time_now.timestamp()


if __name__ == "__main__":
    typer.run(main)
