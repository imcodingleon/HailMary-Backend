"""결과지 재접속 링크 이메일 템플릿.

비로그인 사용자가 결제 후 결과지 다시 보기 위해 이메일로 받는 링크.
share_code(UUID4 hex)가 URL에 박혀 있음 — order_id 노출 없음.
"""

from __future__ import annotations

from datetime import datetime


def _format_expires_date(expires_at: datetime) -> str:
    """expires_at → "2026년 6월 12일" 형식."""
    return f"{expires_at.year}년 {expires_at.month}월 {expires_at.day}일"


def build_result_link_email(
    *,
    share_code: str,
    character: str,
    expires_at: datetime,
    base_url: str = "https://dohwaseonsaju.com",
) -> tuple[str, str, str]:
    """결과지 재접속 링크 이메일 (subject, html, text) 반환.

    Args:
        share_code: PaidReport.share_code (UUID4 hex).
        character: "yeonwoo" 또는 "doyoon".
        expires_at: 결제 만료일 (재접속 가능 기한).
        base_url: 서비스 도메인 (기본 운영). 테스트에선 staging URL 주입.

    Returns:
        (subject, html_body, text_body)
    """
    link = f"{base_url}/saju/result/{share_code}"
    expires_str = _format_expires_date(expires_at)
    char_label = "강연우" if character == "yeonwoo" else "한도윤"

    subject = "도화선 — 너의 사주 결과지가 준비됐어"

    text_body = f"""안녕,

{char_label}의 결과지가 다 완성됐어.

아래 링크에서 결과지를 다시 볼 수 있어.
{link}

이 링크는 {expires_str}까지 열려 있어.
그 후에는 다시 결제해야 새 결과지를 받을 수 있어.

— 도화선
"""

    html_body = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>도화선 결과지</title>
</head>
<body style="margin:0;padding:0;background:#151513;font-family:'Pretendard',-apple-system,sans-serif;">
  <div style="max-width:480px;margin:0 auto;padding:40px 24px;color:#d8d6d0;">
    <h1 style="font-family:'Nanum Myeongjo',serif;color:#E8C9A0;font-size:24px;letter-spacing:0.1em;text-align:center;margin-bottom:8px;">
      도화선
    </h1>
    <p style="text-align:center;color:#888;font-size:13px;margin-bottom:32px;">
      導火線 · 桃花煞
    </p>

    <div style="background:#1a1715;border:0.5px solid rgba(200,168,112,0.30);border-radius:12px;padding:24px;margin-bottom:24px;">
      <p style="color:#d8d6d0;font-size:15px;line-height:1.8;margin:0 0 16px 0;">
        안녕,<br/>
        <strong style="color:#E8C9A0;">{char_label}</strong>의 결과지가 다 완성됐어.
      </p>
      <p style="color:#b0aea4;font-size:14px;line-height:1.8;margin:0 0 24px 0;">
        아래 버튼으로 결과지를 다시 볼 수 있어.
      </p>

      <div style="text-align:center;margin:32px 0;">
        <a href="{link}"
           style="display:inline-block;background:#E8C9A0;color:#0a0a09;text-decoration:none;
                  padding:14px 32px;border-radius:8px;font-weight:600;font-size:15px;">
          결과지 보러 가기
        </a>
      </div>

      <p style="color:#666;font-size:12px;line-height:1.6;margin:24px 0 0 0;text-align:center;">
        링크가 안 열리면 아래 주소를 직접 복사해.<br/>
        <span style="color:#888;word-break:break-all;">{link}</span>
      </p>
    </div>

    <p style="color:#666;font-size:12px;line-height:1.6;text-align:center;">
      이 링크는 <strong style="color:#888;">{expires_str}</strong>까지 열려 있어.<br/>
      그 후에는 다시 결제해야 새 결과지를 받을 수 있어.
    </p>

    <p style="color:#444;font-size:11px;text-align:center;margin-top:32px;">
      — 도화선 (dohwaseonsaju.com)
    </p>
  </div>
</body>
</html>"""

    return subject, html_body, text_body
