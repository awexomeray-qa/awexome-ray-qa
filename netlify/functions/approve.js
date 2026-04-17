const crypto = require('crypto');

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405 };

  const { id, name, email } = JSON.parse(event.body);

  // 토큰 생성
  const token = crypto.randomBytes(32).toString('hex');

  // Supabase 업데이트
  const sbRes = await fetch(
    `${process.env.SUPABASE_URL}/rest/v1/access_requests?id=eq.${id}`,
    {
      method: 'PATCH',
      headers: {
        'apikey': process.env.SUPABASE_KEY,
        'Authorization': `Bearer ${process.env.SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ status: 'approved', token, approved_at: new Date().toISOString() })
    }
  );

  if (!sbRes.ok) {
    return { statusCode: 500, body: JSON.stringify({ error: 'DB 업데이트 실패' }) };
  }

  // 접근 링크
  const accessUrl = `${process.env.SITE_URL}/awexome_ray_qa_final.html?token=${token}`;

  // 투자자에게 이메일 발송
  const emailRes = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`
    },
    body: JSON.stringify({
      from: 'aweXome Ray IR <ir@awexomeray.com>',
      to: [email],
      subject: '[aweXome Ray] 투자자 Q&A 열람 링크가 발송되었습니다',
      html: `
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px">
          <h2 style="color:#0a0a0f;margin-bottom:8px">안녕하세요, ${name}님</h2>
          <p style="color:#666;margin-bottom:24px;line-height:1.6">
            aweXome Ray 투자자 Q&A 포털 열람이 승인되었습니다.<br>
            아래 버튼을 클릭하여 자료를 열람하세요.
          </p>
          <a href="${accessUrl}" style="display:inline-block;padding:14px 28px;background:#c8f55a;color:#0a0a0f;border-radius:8px;text-decoration:none;font-weight:700;font-size:15px">Q&amp;A 열람하기</a>
          <p style="margin-top:24px;font-size:12px;color:#999;line-height:1.6">
            본 링크는 신청하신 분 개인용입니다.<br>
            문의사항은 ir@awexomeray.com 으로 연락 주세요.
          </p>
        </div>
      `
    })
  });

  if (!emailRes.ok) {
    return { statusCode: 500, body: JSON.stringify({ error: '이메일 발송 실패' }) };
  }

  return { statusCode: 200, body: JSON.stringify({ ok: true, token }) };
};
