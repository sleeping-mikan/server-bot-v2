#!ignore
from ..common import *
#!end-ignore


class SendDiscordSelfServer:
    # クラススコープで状態を保持
    _download_registry: dict[str, tuple[str, float]] = {}
    _lock = asyncio.Lock()
    _ttl_default = 300  # 5分

    @classmethod
    async def register_download(cls, directory_path: str, ttl_seconds: int = None) -> str:
        if not os.path.isdir(directory_path):
            raise ValueError("指定されたパスはディレクトリではありません")
        ttl = ttl_seconds if ttl_seconds else cls._ttl_default
        token = uuid.uuid4().hex
        expire_at = datetime.now() + timedelta(seconds=ttl)
        async with cls._lock:
            cls._download_registry[token] = (directory_path, expire_at)
        return f"http://localhost:{web_port}/download/{token}"

    @classmethod
    async def _cleanup_loop(cls):
        while True:
            now = datetime.now()
            async with cls._lock:
                expired = [t for t, (_, exp) in cls._download_registry.items() if now > exp]
                for t in expired:
                    del cls._download_registry[t]
            await asyncio.sleep(30)

    @classmethod
    async def download(cls, token: str):
        async with cls._lock:
            entry = cls._download_registry.pop(token, None)
        if not entry:
            raise HTTPException(status_code=404, detail="リンクが無効または既に使用されました")
        directory_path, expire_at = entry
        if 	datetime.now() > expire_at > expire_at:
            raise HTTPException(status_code=410, detail="このリンクは期限切れです")

        # zipstreamでリアルタイムZIP
        z = zipstream.ZipStream()
        for root, _, files in os.walk(directory_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=directory_path)
                z.add(full_path, arcname)

        filename = os.path.basename(directory_path) or "download"
        return StreamingResponse(
            z,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}.zip"'}
        )

    @classmethod
    def create_app(cls) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            task = asyncio.create_task(cls._cleanup_loop())
            yield
            task.cancel()

        app = FastAPI(lifespan=lifespan)
        app.add_api_route("/download/{token}", cls.download, methods=["GET"])
        return app
