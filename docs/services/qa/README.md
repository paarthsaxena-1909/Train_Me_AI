# Q&A service

The Q&A flow lets an authenticated agent submit one product question and receive one answer. Each interaction is stored in the existing `agent_queries` table with its selected product.

The response generator is intentionally mocked. `QAService` owns the seam where the future AI analysis layer will be called; replace `MOCK_RESPONSE` and that service step with the real provider later. This is a single request/answer interaction, not a conversational chatbot, and history is not shown in the current UI.

Q&A does not query product tables directly. It asks the product domain for context through `ProductContextPort`, the internal cross-domain boundary (which can be registered with the mediator as services are split). The product domain owns product existence and catalogue reads; Q&A owns validation of the question, response generation, and persistence in `agent_queries`.

`ProductContextAdapter` is intentionally a thin adapter: it delegates to
`ProductsService.get_context()` and does not implement a second product lookup
flow.

## API

- `POST /api/v1/queries` (agent role): `{ "product_id": 1, "query": "..." }`
- Returns `201`: `{ "id": 1, "product_id": 1, "query": "...", "response": "..." }`
- Returns `404` when the selected product does not exist.
