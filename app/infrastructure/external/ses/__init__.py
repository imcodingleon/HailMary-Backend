"""AWS SES 이메일 발송 클라이언트.

비로그인 사용자의 재접속 링크 발송용 (PaidReport.share_code 기반).
Amplitude 클라이언트 패턴 차용 — fire-and-forget, 예외는 호출자가 swallow.
"""
