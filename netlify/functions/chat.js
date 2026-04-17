exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405 };
  
  const body = JSON.parse(event.body);
  
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': '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',
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify(body)
  });
  
  const data = await res.json();
  return {
    statusCode: 200,
    headers: {'Access-Control-Allow-Origin': '*'},
    body: JSON.stringify(data)
  };
};
