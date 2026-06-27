/**
 * reCAPTCHA Enterprise frontend hook (stub).
 * Wire into login/register when Firebase Auth UI ships.
 * Set NEXT_PUBLIC_RECAPTCHA_SITE_KEY in frontend/.env.local for production.
 */

const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY ?? "";

export function isRecaptchaConfigured(): boolean {
  return siteKey.length > 0;
}

export function getRecaptchaSiteKey(): string {
  return siteKey;
}

/**
 * Execute reCAPTCHA Enterprise and return a token for backend verify.
 * Requires grecaptcha.enterprise script on the page when fully wired.
 */
export async function executeRecaptcha(
  action: string,
): Promise<string | null> {
  if (!isRecaptchaConfigured()) {
    return null;
  }
  const grecaptcha = (
    globalThis as typeof globalThis & {
      grecaptcha?: {
        enterprise?: {
          execute: (key: string, opts: { action: string }) => Promise<string>;
        };
      };
    }
  ).grecaptcha;

  if (!grecaptcha?.enterprise?.execute) {
    console.warn(
      "reCAPTCHA stub: load enterprise script and set NEXT_PUBLIC_RECAPTCHA_SITE_KEY",
    );
    return null;
  }

  return grecaptcha.enterprise.execute(siteKey, { action });
}
