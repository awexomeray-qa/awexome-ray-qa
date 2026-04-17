exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405 };

  const { name, company, email } = JSON.parse(event.body);

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`
    },
    body: JSON.stringify({
      from: 'aweXome Ray IR <onboarding@resend.dev>',
      to: [process.env.ADMIN_EMAIL],
      subject: `[IR 열람 신청] ${name} / ${company || '소속 미입력'}`,
      html: `
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px">
          <h2 style="color:#0a0a0f;margin-bottom:16px">새 열람 신청이 접수되었습니다</h2>
          <table style="width:100%;border-collapse:collapse">
            <tr><td style="padding:8px 0;color:#666;width:80px">성함</td><td style="padding:8px 0;font-weight:500">${name}</td></tr>
            <tr><td style="padding:8px 0;color:#666">소속</td><td style="padding:8px 0">${company || '미입력'}</td></tr>
            <tr><td style="padding:8px 0;color:#666">이메일</td><td style="padding:8px 0">${email}</td></tr>
          </table>
          <div style="margin-top:24px;padding:16px;background:#f5f5f5;border-radius:8px">
            <p style="margin:0;font-size:13px;color:#666">아래 링크에서 신청을 승인하세요:</p>
            <a href="${process.env.SITE_URL}/admin_requests.html" style="display:inline-block;margin-top:8px;padding:10px 20px;background:#c8f55a;color:#0a0a0f;border-radius:6px;text-decoration:none;font-weight:600;font-size:13px">신청 관리 페이지 열기</a>
          </div>
        </div>
      `
    })
  });

  return { statusCode: 200, body: JSON.stringify({ ok: true }) };
};
