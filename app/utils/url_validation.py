import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import HTTPException


def _resolve_host_ips(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, None)
        return list({info[4][0] for info in infos})
    except socket.gaierror:
        raise HTTPException(
            status_code=400, detail="Could not resolve hostname"
        )


def _is_forbidden_ip(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_reserved
        or addr.is_unspecified
    )


def validate_external_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(
            status_code=400, detail="Only http and https URLs are allowed"
        )

    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL")

    hostname = parsed.hostname.lower()

    if hostname == "localhost":
        raise HTTPException(
            status_code=400, detail="Local addresses are not allowed"
        )
 
    ips = _resolve_host_ips(hostname)

    for ip in ips:
        if _is_forbidden_ip(ip):
            raise HTTPException(
                status_code=400,
                detail="Private or local network addresses are not allowed",
            )
