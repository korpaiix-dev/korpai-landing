/**
 * Minimal multi-channel message normalizer for combat-sports SME chatbots.
 *
 * Unifies inbound webhooks from Line OA, WhatsApp Business, Instagram DM,
 * Facebook Messenger, WeChat OA, KakaoTalk into a single internal envelope so
 * the LLM router sees one profile per customer across all channels.
 *
 * KORP AI Automation, 2026-05-30. MIT.
 */

const HANDLERS = {
  line: (raw) => raw.events?.map((e) => ({
    channel: 'line',
    user_id: e.source?.userId,
    text: e.message?.text,
    ts: e.timestamp,
    raw: e,
  })) || [],

  whatsapp: (raw) => raw.entry?.[0]?.changes?.[0]?.value?.messages?.map((m) => ({
    channel: 'whatsapp',
    user_id: m.from,
    text: m.text?.body,
    ts: Number(m.timestamp) * 1000,
    raw: m,
  })) || [],

  instagram: (raw) => raw.entry?.flatMap((e) => e.messaging || []).map((m) => ({
    channel: 'instagram',
    user_id: m.sender?.id,
    text: m.message?.text,
    ts: m.timestamp,
    raw: m,
  })) || [],

  messenger: (raw) => raw.entry?.flatMap((e) => e.messaging || []).map((m) => ({
    channel: 'messenger',
    user_id: m.sender?.id,
    text: m.message?.text,
    ts: m.timestamp,
    raw: m,
  })) || [],

  wechat: (raw) => [{
    channel: 'wechat',
    user_id: raw.FromUserName,
    text: raw.Content,
    ts: Number(raw.CreateTime) * 1000,
    raw,
  }],

  kakao: (raw) => [{
    channel: 'kakao',
    user_id: raw.userRequest?.user?.id,
    text: raw.userRequest?.utterance,
    ts: Date.now(),
    raw,
  }],
};

function normalize(channel, raw) {
  const h = HANDLERS[channel];
  if (!h) throw new Error(`Unknown channel: ${channel}`);
  return h(raw).filter((msg) => msg.text);
}

// Cross-channel identity: caller maps (channel, user_id) to internal customer_id.
// Recommended: store mapping in Redis with TTL aligned to consent window.
function profileKey(channel, user_id) {
  return `customer:${channel}:${user_id}`;
}

module.exports = { normalize, profileKey };
