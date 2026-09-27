from __future__ import annotations
import json, os, urllib.parse, urllib.request
from dataclasses import dataclass

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"

@dataclass(frozen=True)
class YouTubeUploadResult:
    video_id: str
    url: str

class YouTubePublisher:
    """Minimal YouTube Data API v3 resumable uploader using a refresh token."""
    def __init__(self, client_id=None, client_secret=None, refresh_token=None):
        self.client_id=client_id or os.getenv("YOUTUBE_CLIENT_ID")
        self.client_secret=client_secret or os.getenv("YOUTUBE_CLIENT_SECRET")
        self.refresh_token=refresh_token or os.getenv("YOUTUBE_REFRESH_TOKEN")
        if not all((self.client_id,self.client_secret,self.refresh_token)):
            raise RuntimeError("YouTube OAuth is not configured: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN are required")

    def _access_token(self):
        body=urllib.parse.urlencode({"client_id":self.client_id,"client_secret":self.client_secret,"refresh_token":self.refresh_token,"grant_type":"refresh_token"}).encode()
        req=urllib.request.Request(TOKEN_URL,data=body,headers={"Content-Type":"application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req,timeout=30) as r:
            payload=json.load(r)
        token=payload.get("access_token")
        if not token: raise RuntimeError("Google token refresh returned no access_token")
        return token

    def upload(self, video_path, *, title, description="", tags=None, privacy_status="private", publish_at=None):
        if privacy_status not in {"private","unlisted","public"}: raise ValueError("invalid privacy_status")
        if publish_at and privacy_status != "private": raise ValueError("scheduled videos must use privacy_status='private'")
        token=self._access_token()
        metadata={"snippet":{"title":title,"description":description,"tags":tags or [],"categoryId":"22"},"status":{"privacyStatus":privacy_status,"selfDeclaredMadeForKids":False}}
        if publish_at: metadata["status"]["publishAt"]=publish_at
        req=urllib.request.Request(UPLOAD_URL,data=json.dumps(metadata).encode(),method="POST",headers={"Authorization":f"Bearer {token}","Content-Type":"application/json; charset=UTF-8","X-Upload-Content-Type":"video/mp4"})
        with urllib.request.urlopen(req,timeout=30) as r:
            upload_url=r.headers.get("Location")
        if not upload_url: raise RuntimeError("YouTube did not return a resumable upload URL")
        with open(video_path,"rb") as f: data=f.read()
        req=urllib.request.Request(upload_url,data=data,method="PUT",headers={"Authorization":f"Bearer {token}","Content-Type":"video/mp4","Content-Length":str(len(data))})
        with urllib.request.urlopen(req,timeout=300) as r: payload=json.load(r)
        video_id=payload.get("id")
        if not video_id: raise RuntimeError("YouTube upload completed without a video id")
        return YouTubeUploadResult(video_id, f"https://www.youtube.com/watch?v={video_id}")
