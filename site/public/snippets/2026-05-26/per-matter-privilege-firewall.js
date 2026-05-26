/**
 * per-matter-privilege-firewall.js
 *
 * Why: Thai law firms MUST isolate matter A's documents from matter B at the
 * retrieval layer. A single shared vector store = guaranteed conflict of
 * interest and breach of ม.16 ข้อบังคับสภาทนายความ. This wraps a Qdrant /
 * Pinecone client so that every search() call is namespaced by matter_id,
 * and any cross-matter chunk is rejected at the middleware before it can
 * ever reach the LLM context window.
 *
 * Use this in front of LangChain/Llamaindex retrievers; never bypass it.
 *
 * Author: KORP AI — https://korpai.co
 * License: MIT
 */

/**
 * @param {{ search: (args: any) => Promise<any[]> }} vectorClient
 * @param {{ matterId: string, userId: string, allowed: (matterId: string, userId: string) => Promise<boolean> }} ctx
 */
function makePrivilegeRetriever(vectorClient, ctx) {
  if (!ctx?.matterId) throw new Error('matterId is required');

  return {
    async retrieve(query, k = 8) {
      const allowed = await ctx.allowed(ctx.matterId, ctx.userId);
      if (!allowed) {
        // Audit-trail this: someone tried to read a matter they aren't on.
        throw new Error(
          `privilege-violation: user=${ctx.userId} matter=${ctx.matterId}`
        );
      }

      // Per-matter collection name. NEVER mix matters in one collection.
      const collection = `matter_${ctx.matterId}`;

      const results = await vectorClient.search({
        collection,
        query,
        limit: k,
        // Belt + braces: even within the collection, filter by matter tag.
        filter: { must: [{ key: 'matter_id', match: { value: ctx.matterId } }] },
      });

      // Final guardrail: drop any chunk whose payload disagrees with ctx.
      return results.filter((r) => r.payload?.matter_id === ctx.matterId);
    },
  };
}

module.exports = { makePrivilegeRetriever };
