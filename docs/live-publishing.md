# Live Pinterest publishing gate

Media Engine has a production transport boundary but live publication is not globally enabled.

A live Pin requires all of the following:
1. content passes QA;
2. the content category exactly matches the configured board category;
3. a public HTTPS media URL is supplied;
4. the Pinterest API call succeeds and returns a Pin ID;
5. idempotency prevents duplicate sends.

Current connected boards are deliberately treated as narrow destinations:
- Wedding Planning Templates -> wedding
- Contractor Business Tools -> contractor

Generic small-business automation content must not be forced into either board. It should wait for a correctly scoped board and suitable original media.

Representative free-model validation on 2026-09-10 also showed that too-small generation token budgets can be consumed by model reasoning and yield no usable content. The OpenRouter adapter now rejects truncated/null output and uses a larger default completion budget.
