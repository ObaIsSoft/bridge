import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Next.js 16 Proxy Configuration
 * This replaces the deprecated middleware.ts convention.
 * 
 * Performance: Runs on the Node.js runtime by default.
 * Security: Hardened against x-middleware-subrequest bypass attacks.
 */
export async function proxy(request: NextRequest) {
    const response = NextResponse.next();

    // 1. Security Headers (HSTS, CSP, etc.)
    // Data sensitivity requires strict protection
    response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('X-Frame-Options', 'DENY');
    response.headers.set('X-XSS-Protection', '1; mode=block');
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

    // 2. Protect against x-middleware-subrequest bypass
    // Modern Next.js security best practice
    if (request.headers.has('x-middleware-subrequest')) {
        return new NextResponse('Internal Server Error', { status: 500 });
    }

    // 3. Basic Audit Logging (Sensitive Data Access)
    if (process.env.NODE_ENV === 'development') {
        const url = request.nextUrl.pathname;
        const method = request.method;
        console.log(`[PROXY] ${method} ${url} - ${new Date().toISOString()}`);
    }

    return response;
}

// Ensure the proxy runs for all relevant routes
export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes) - Managed by the FastAPI backend
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
};
