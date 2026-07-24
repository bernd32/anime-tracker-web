import type { NextRequest } from 'next/server';

const DEFAULT_API_PROXY_TARGET = 'http://api:43968/api/v1';
const HOP_BY_HOP_REQUEST_HEADERS = new Set([
  'connection',
  'content-length',
  'host',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
]);
const HOP_BY_HOP_RESPONSE_HEADERS = new Set([
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
]);

export const dynamic = 'force-dynamic';

function getApiProxyTarget() {
  const configured = process.env.API_PROXY_TARGET?.trim();
  return (configured && configured.length > 0 ? configured : DEFAULT_API_PROXY_TARGET).replace(/\/+$/, '');
}

function buildTargetUrl(path: string[], request: NextRequest) {
  const target = new URL(`${getApiProxyTarget()}/${path.join('/')}`);
  target.search = request.nextUrl.search;
  return target;
}

function copyRequestHeaders(request: NextRequest) {
  const headers = new Headers();

  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP_REQUEST_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  return headers;
}

function copyResponseHeaders(upstream: Response) {
  const headers = new Headers();

  upstream.headers.forEach((value, key) => {
    const normalizedKey = key.toLowerCase();
    if (!HOP_BY_HOP_RESPONSE_HEADERS.has(normalizedKey) && normalizedKey !== 'set-cookie') {
      headers.set(key, value);
    }
  });

  // A successful login sends separate session and CSRF cookies. `forEach` exposes
  // them as one combined value in Node's Fetch implementation, which browsers do
  // not interpret as two cookies. Forward each Set-Cookie field independently.
  for (const cookie of upstream.headers.getSetCookie()) {
    headers.append('set-cookie', cookie);
  }

  return headers;
}

async function proxyRequest(request: NextRequest, path: string[]) {
  const method = request.method.toUpperCase();
  const body = method === 'GET' || method === 'HEAD' ? undefined : await request.arrayBuffer();
  const upstream = await fetch(buildTargetUrl(path, request), {
    method,
    headers: copyRequestHeaders(request),
    body,
    cache: 'no-store',
    redirect: 'manual',
  });

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: copyResponseHeaders(upstream),
  });
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PUT(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function OPTIONS(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function HEAD(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}
