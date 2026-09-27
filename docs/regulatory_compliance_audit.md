# Enterprise Pharma Copilot — Regulatory & OPDP Compliance Audit Report  
**Scope:** Reference architecture and required OPDP Compliance Guardrail rules.  
**Audit status:** **Design evidence was not provided** (architecture diagrams, endpoint definitions, label data model, prompt templates, retrieval controls, rendering specifications, and test evidence were unavailable). Therefore, no implementation can be certified compliant. This report identifies the controls that must exist and specifies deterministic guardrail logic suitable for implementation and validation.

## 1. Regulatory control objectives

| Control area | Required outcome |
|---|---|
| Fair Balance — 21 CFR § 202.1 | Promotional efficacy statements must be accompanied by appropriately prominent, label-supported risk information. Risk content cannot be hidden behind a link, collapsed disclosure, hover state, or separate workflow. |
| Medical Affairs / MSL firewall | A request reasonably construed as seeking information about an unapproved use, population, dose, route, regimen, or combination must not receive a generated promotional or medical answer from the Copilot. It must be intercepted and routed as an unsolicited Medical Information Request (MIR). |
| HIPAA Safe Harbor / minimum-cell policy | No analytic output may disclose a cell where \(N < 11\). Queries must also resist differencing, overlapping cohorts, and repeated-query attacks. |
| 21 CFR Part 11 | Guardrail configuration, approved-label sources, decisions, overrides, and audit events require attributable, time-stamped, tamper-evident audit records and controlled change management. |

**Important qualification:** A regular expression can identify high-risk language, but cannot determine whether a use is off-label or whether a communication is fairly balanced. Those decisions require a version-controlled approved-label knowledge base and a structured content/risk rendering policy. Regex is a deterministic detection layer and must not be the sole compliance decision-maker.

---

# 2. Required guardrail architecture

The OPDP Compliance Guardrail must run at **both** boundaries:

1. **Inbound request guardrail**
   - Classify request type.
   - Detect possible off-label/MIR requests.
   - Remove or tokenize direct identifiers before logging or downstream processing.
   - Block or route before retrieval, generation, tool calling, CRM creation, or analytics execution.

2. **Retrieval and tool guardrail**
   - Permit retrieval only from approved, versioned sources:
     - current FDA-approved Prescribing Information (PI),
     - FDA-approved Medication Guide, where applicable,
     - approved promotional claims library,
     - Medical Information-approved response library.
   - Prevent unapproved documents, study data, internal slide decks, investigator materials, and uncontrolled web content from entering promotional response generation.
   - Enforce aggregate-query privacy restrictions before data execution.

3. **Outbound response guardrail**
   - Detect benefit claims and risk language.
   - Require a structured, current, product-specific risk component for promotional output.
   - Reject unsupported or comparative claims.
   - Apply response-type-specific routing: promotional, labeled medical information, off-label MIR, pharmacovigilance/adverse-event intake, or privacy refusal.
   - Inspect the final rendered response—not merely draft text—for prominence and accessibility requirements.

4. **Audit and approval control plane**
   - Version every rule, product label, source document, model/prompt release, and decision.
   - Record request hash/token, classification, label version, rule version, retrieval document IDs, guardrail action, output hash, human override identity, reason, and timestamp.
   - Do not log unredacted patient information, free-text identifiers, or unnecessary content in audit records.

---

# 3. Canonical normalization rules

All regex matching must occur only after the following normalization sequence.

```text
1. Reject malformed byte sequences.
2. Unicode normalize: NFKC.
3. Remove Unicode zero-width and directional control characters.
4. Replace all Unicode whitespace runs with one ASCII space.
5. Collapse repeated punctuation to one character, except decimal points and hyphens
   needed by recognized product names or doses.
6. Case-fold using Unicode case folding.
7. Preserve the original input separately only in the protected, access-controlled
   request store; use the normalized/redacted value for routine logs.
```

Recommended implementation:

```text
normalized =
  collapse_spaces(
    remove_bidi_and_zero_width(
      unicode_nfkc(input)
    )
  ).casefold()
```

The pattern syntax below is **PCRE2-compatible**. If using RE2, use the same patterns after removing unsupported inline features if applicable. Product names and indication terms must be regex-escaped before configuration compilation.

---

# 4. Exact regex rules

## 4.1 Configuration variables

The following are not hard-coded strings. They are versioned data from Regulatory-approved product and label records.

```text
PRODUCT_RX         = alternation of generic, brand, approved abbreviations, and common misspellings
INDICATION_RX      = alternation of approved disease/use terms and approved synonyms
POPULATION_RX      = approved population attributes, restrictions, age range, biomarkers, line of therapy, etc.
DOSE_ROUTE_RX      = approved dose, schedule, route, formulation, and administration terms
UNAPPROVED_USE_RX  = controlled ontology of non-approved conditions, populations, dosing,
                     routes, combinations, and clinical settings
```

Example construction:

```regex
(?<product>(?:brandname|genericname|brand\s*name))
```

All product aliases must be reviewed by Regulatory. Do not permit end users or application administrators to alter this list without formal approval and audit trail.

---

## 4.2 Explicit off-label / unapproved-use request

This rule is a **hard intercept**, independent of downstream classifier confidence.

```regex
(?ix)
\b
(?:
    off[-\s]?label
  | unapproved(?:\s+(?:use|indication|dose|dosing|regimen|population|route|combination))?
  | not\s+(?:fda[\s-]?approved|approved|on[-\s]?label)
  | outside\s+(?:the\s+)?label
  | beyond\s+(?:the\s+)?(?:approved\s+)?indication
  | experimental\s+use
  | compassionate\s+use
  | investigational\s+use
)
\b
```

**Action:** `ROUTE_TO_MIR`; do not answer the scientific or treatment question.

---

## 4.3 Treatment, prescribing, and efficacy intent

This identifies a request that could seek an off-label answer. It is not, by itself, sufficient to determine off-label status.

```regex
(?ix)
\b
(?:
    use|using|prescribe|prescribing|start|initiat(?:e|ing|ion)|
    dose|dosing|titrate|titration|administer|administration|
    treat|treating|treatment|manage|managing|prevent|prevention|
    prophylaxis|recommend|recommended|give|giving|
    effective|efficacy|works?|work(?:ing)?|
    indicat(?:e|ed|ion)|approved|
    switch(?:ing)?|combine|combination|add[-\s]?on
)
\b
```

Name: `THERAPEUTIC_INTENT_RX`.

---

## 4.4 Question / information-seeking signal

```regex
(?ix)
(?:^|\b)
(?:
    can|could|should|would|may|is|are|does|do|what|when|where|why|how|
    tell\s+me|please\s+(?:explain|provide|describe)|looking\s+for|
    need\s+(?:information|guidance)|want\s+to\s+know
)
\b
```

Name: `QUESTION_INTENT_RX`.

---

## 4.5 Product-and-use proximity rule

The system must detect product and use references occurring in the same clause or within a bounded token window. Use a maximum span of **160 normalized characters** or **24 tokens**, whichever is smaller.

```regex
(?ix)
(?:
    (?<product>PRODUCT_RX)
    (?:(?![.!?;]).){0,160}?
    (?<intent>THERAPEUTIC_INTENT_RX|UNAPPROVED_USE_RX)
)
|
(?:
    (?<intent>THERAPEUTIC_INTENT_RX|UNAPPROVED_USE_RX)
    (?:(?![.!?;]).){0,160}?
    (?<product>PRODUCT_RX)
)
```

Replace symbolic values with compiled, escaped configuration values.

Name: `PRODUCT_USE_PROXIMITY_RX`.

---

## 4.6 Unapproved population, dose, route, regimen, or combination signals

These are high-risk modifiers. A match becomes an off-label candidate only when associated with a specific product and a treatment/prescribing intent, or when the user explicitly asks about an unapproved use.

```regex
(?ix)
\b
(?:
    pediatric(?:s)?|child(?:ren)?|adolescent(?:s)?|
    pregnant|pregnancy|breast[\s-]?feeding|lactat(?:ing|ion)|
    renal\s+(?:impairment|failure)|hepatic\s+(?:impairment|failure)|
    elderly|geriatr(?:ic|ics)|
    first[-\s]?line|second[-\s]?line|third[-\s]?line|maintenance|
    neoadjuvant|adjuvant|salvage|
    higher[-\s]?dose|lower[-\s]?dose|double[-\s]?dose|
    once\s+(?:daily|weekly|monthly)|twice\s+(?:daily|weekly)|
    intravenous|intravenously|iv|subcutaneous|subcutaneously|sc|
    intramuscular|topical|inhaled|intranasal|
    with\s+\w+|combined\s+with|combination\s+with|add(?:ed)?\s+to
)
\b
```

Name: `HIGH_RISK_USE_MODIFIER_RX`.

**Note:** The general combination expressions must be correlated with a medication/entity recognizer. The phrase `with food` must not be treated as a product-combination request. A configuration allowlist is required for labeled combinations and administration instructions.

---

## 4.7 Benefit / efficacy claim detection

This is an **outbound backstop**, not an approval mechanism. All promotional benefits should be emitted by structured approved-claim components, rather than generated ad hoc.

```regex
(?ix)
\b
(?:
    (?:significant(?:ly)?|clinically\s+meaningful(?:ly)?)\s+
    (?:improv(?:e|ed|es|ing|ement)|reduc(?:e|ed|es|ing|tion)|increase(?:d|s|ing)?)
  | improve(?:d|s|ing)?\s+(?:survival|symptoms?|outcomes?|response|quality\s+of\s+life)
  | reduce(?:d|s|ing)?\s+(?:risk|mortality|hospitali[sz]ation|progression|symptoms?)
  | prolong(?:ed|s|ing)?\s+(?:survival|remission|time\s+to\s+progression)
  | superior(?:ity)?|better\s+than|more\s+effective
  | proven|demonstrated|shown\s+to|clinically\s+proven
  | works?\s+(?:for|in)|effective\s+(?:for|in)
  | response\s+rate|remission\s+rate|hazard\s+ratio|odds\s+ratio
)
\b
```

Name: `BENEFIT_CLAIM_RX`.

**Required supplemental structured check:** Every matched claim must map to an approved claim ID, PI section, study/source reference, claim population, endpoint, comparator, and approved wording constraints. If no mapping exists, reject the response.

---

## 4.8 Risk-language detection

```regex
(?ix)
\b
(?:
    boxed\s+warning|warning(?:s)?|precaution(?:s)?|
    contraindicat(?:ed|ion|ions)|
    adverse\s+(?:event|events|reaction|reactions)|
    side\s+effect(?:s)?|serious\s+(?:risk|risks|adverse\s+(?:event|events))|
    risk(?:s)?\s+of|may\s+(?:cause|increase\s+the\s+risk\s+of)|
    fatal|death|life[-\s]?threatening|
    monitor(?:ing)?|discontinue|stop\s+(?:treatment|therapy|the\s+drug)|
    avoid\s+(?:use|using)|do\s+not\s+(?:use|take)|
    hypersensitiv(?:ity|ities)|anaphylaxis
)
\b
```

Name: `RISK_LANGUAGE_RX`.

This pattern only confirms textual risk language. It does **not** prove that the correct, current, product-specific risks were communicated.

---

## 4.9 Identifier detection for pre-log redaction

Regex detection is only one component of HIPAA protection; entity recognition and data-classification controls are also required.

```regex
# Email
(?ix)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,63}\b

# US phone number
(?x)\b(?:\+?1[-.\s]?)?(?:\(?[2-9]\d{2}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b

# US SSN
(?x)\b(?!000|666|9\d\d)\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b

# IPv4
(?x)\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b

# MRN/record number only when context-labelled
(?ix)\b(?:mrn|medical\s+record(?:\s+number)?|patient\s*(?:id|identifier)|member\s*id)
\s*[:#-]?\s*[a-z0-9][a-z0-9\-]{4,31}\b
```

Dates, names, addresses, account numbers, biometric data, photographs, device identifiers, URLs, and free-text clinical narratives require semantic detection and policy enforcement. A regex-only privacy control is not sufficient.

---

# 5. Exact decision logic

## 5.1 Inbound classification and Medical Affairs firewall

```pseudo
function evaluateInbound(request, sessionContext):
    text = normalize(request.text)
    redactedText = redactIdentifiers(text)

    if matches(text, EXPLICIT_OFF_LABEL_RX):
        return routeMIR(
            reason = "EXPLICIT_UNAPPROVED_USE_REQUEST",
            logText = redactedText
        )

    entities = extractEntities(text)
    # entities include product, condition, population, dose, route,
    # regimen, combination agent, disease stage, and treatment intent.

    product = resolveApprovedProduct(entities.product, sessionContext.product)
    therapeuticIntent =
        matches(text, THERAPEUTIC_INTENT_RX) OR
        matches(text, QUESTION_INTENT_RX) AND entities.containsClinicalTopic

    if product is not null AND therapeuticIntent:
        requestedUse = normalizeUse(
            condition = entities.condition,
            population = entities.population,
            dose = entities.dose,
            route = entities.route,
            regimen = entities.regimen,
            combination = entities.combination,
            treatmentSetting = entities.setting
        )

        labelMatch = approvedLabelService.match(
            productNdcOrProductId = product.id,
            requestedUse = requestedUse,
            labelVersion = currentEffectiveLabel(product.id)
        )

        if labelMatch.status == "NOT_APPROVED":
            return routeMIR(
                reason = "OFF_LABEL_USE_DETECTED",
                product = product.id,
                labelVersion = labelMatch.labelVersion,
                logText = redactedText
            )

        if labelMatch.status in ["AMBIGUOUS", "INSUFFICIENT_CONTEXT", "LABEL_UNAVAILABLE"]:
            return routeMIR(
                reason = "POSSIBLE_OFF_LABEL_USE_REQUIRES_MEDICAL_REVIEW",
                product = product.id,
                logText = redactedText
            )

    if containsAdverseEventOrProductComplaint(text):
        return routePharmacovigilance(
            logText = redactedText,
            preserveRequiredSafetyIntakeFields = true
        )

    return continueToApprovedResponseWorkflow()
```

### Mandatory firewall behavior

For `ROUTE_TO_MIR`, the Copilot must:

- **Not** provide dosing, efficacy, safety interpretation, treatment recommendations, literature summaries, study results, or comparisons related to the unapproved use.
- Provide only a neutral routing statement, for example:

> “Your question may concern a use that is not addressed in the approved product labeling. I cannot provide information on that use here. I can route this as an unsolicited Medical Information Request to the Medical Information team.”

- Collect only the minimum information necessary to fulfill the request, with appropriate consent and privacy notice.
- Create a case only after consent where required by policy.
- Maintain a clear separation between Commercial/Promotional systems and Medical Information case-management systems.
- Ensure Commercial users cannot use MIR data to target, profile, or promote to requesters.

### Fail-closed rule

If product-label matching cannot determine whether the requested use is on-label, the request is **not eligible for automated substantive response**. It routes to MIR.

---

## 5.2 Fair Balance decision logic

A benefit-containing promotional response must be rejected unless it is assembled from approved components and contains required risk content.

```pseudo
function evaluateOutbound(responseDraft, context):
    rendered = renderToTargetChannel(responseDraft, context.channel)

    benefits = detectBenefits(rendered.text)
    risks = detectRisks(rendered.text)

    if context.responseType == "PROMOTIONAL":
        if benefits.count > 0:
            if not allBenefitsMapToApprovedClaims(benefits, context.product, context.labelVersion):
                reject("UNSUPPORTED_OR_UNAPPROVED_BENEFIT_CLAIM")

            requiredRiskSet = riskLibrary.requiredRiskSet(
                product = context.product,
                labelVersion = context.labelVersion,
                audience = context.audience,
                channel = context.channel,
                claims = benefits.approvedClaimIds
            )

            if not containsExactApprovedRiskComponent(rendered, requiredRiskSet):
                reject("MISSING_REQUIRED_RISK_DISCLOSURE")

            if not meetsProminenceRules(rendered, benefitBlocks, riskBlocks):
                reject("RISK_NOT_COMPARABLY_PROMINENT")

            if containsUnqualifiedSuperiorityOrAbsoluteClaim(rendered.text):
                reject("UNQUALIFIED_COMPARATIVE_OR_ABSOLUTE_CLAIM")

    if containsOffLabelContent(rendered, context.product, context.labelVersion):
        rejectAndRouteMIR("OUTBOUND_OFF_LABEL_CONTENT")

    return approveForDelivery()
```

## 5.3 Minimum fair-balance rendering requirements

The following are conservative internal control requirements intended to operationalize fair balance. They are not a substitute for Regulatory review.

### Text/web/chat

Where a benefit claim appears:

1. The corresponding product-specific risk component must be displayed:
   - in the **same response**;
   - with no click, hover, expansion, navigation, login, or external link required;
   - before the user can submit another prompt or receive a different response;
   - directly following the benefit block, or in a persistent adjacent panel visible in the same viewport.

2. Risk prominence must meet all of the following:
   - same font family as benefit text;
   - font size at least **100%** of the benefit text’s computed font size;
   - contrast ratio at least **4.5:1** against background;
   - no lower opacity, blur, truncation, clipping, collapsed accordion, tooltip-only placement, or auto-dismiss behavior;
   - risk block heading must be at least the same computed font size and font weight as the benefit heading;
   - no benefit headline may appear alone in a notification, search snippet, card preview, email subject line, or export where the required risk block is excluded.

3. Risks must be sourced from the current approved risk component associated with the approved claim and product label version. Free-form model paraphrasing of contraindications, warnings, or serious risks is prohibited for promotional responses.

### Audio/video

Where benefit statements are presented:
- Risk information must be audible, intelligible, and in the same asset.
- Voice speed for risk content must not exceed the voice speed used for benefits.
- Risk audio must not use materially lower volume, music masking, or reduced clarity.
- Required risk content cannot be relegated only to captions, end cards, or a linked PI.

### Structured claim control

Every approved promotional claim object must contain:

```json
{
  "claim_id": "REG-APPROVED-CLAIM-ID",
  "product_id": "PRODUCT-ID",
  "label_version": "PI-EFFECTIVE-DATE-OR-VERSION",
  "approved_text": "Exact approved claim wording",
  "population": "Approved population",
  "endpoint": "Approved endpoint",
  "study_reference": "Approved source reference",
  "required_risk_component_id": "RISK-COMPONENT-ID",
  "allowed_channels": ["chat", "web", "email"],
  "expiration_or_review_date": "YYYY-MM-DD"
}
```

If any field is absent, expired, or mismatched to the product/label, the benefit claim must not be delivered.

---

# 6. HIPAA Safe Harbor and \(N \geq 11\) output controls

## 6.1 Exact primary cell-suppression rule

```pseudo
function releaseCell(cell):
    if cell.distinctPersonCount < 11:
        return SUPPRESS
    return ELIGIBLE_FOR_FURTHER_DISCLOSURE_CHECKS
```

Under the stated policy, values from **0 through 10 must not be released** as analytic cells. Suppressed cells must display a neutral marker such as:

```text
Suppressed — insufficient population size
```

Do not return:
- exact count,
- percentage,
- numerator/denominator,
- rate,
- confidence interval,
- min/max,
- raw record list,
- chart tooltip,
- downloadable value,
- error message revealing the count,
- natural-language restatement that permits inference.

## 6.2 Denominator, percentage, and small-group rule

A percentage may be released only if both numerator and denominator satisfy the policy threshold:

```pseudo
if numeratorN < 11 OR denominatorN < 11:
    suppress(metric)
```

For percentages that could disclose a small numerator through rounding, apply:

```pseudo
if inferredNumeratorFromDisplayedPercentage(percentage, denominator) < 11:
    suppress(metric)
```

The preferred implementation is not to return percentages for any table where the system cannot prove that every displayed percentage is non-inferential.

## 6.3 Complementary suppression rule

Suppressing only the small cell is insufficient when totals reveal it.

```pseudo
function applyComplementarySuppression(table):
    suppress all cells with N < 11

    while any suppressed cell can be derived from:
        row totals, column totals, grand totals,
        percentages, prior released overlapping tables,
        filters, drill-downs, exports, or API responses:
            suppress the minimum additional eligible cell(s)
            needed to prevent derivation

    return table
```

The query engine must evaluate the full result set, including totals and all dimensions, before rendering any output.

## 6.4 Differencing and overlap protection

The system must reject or coarsen queries where a user can subtract one valid result from another to derive an \(N < 11\) cell.

Required controls:

```pseudo
1. Minimum cohort size: no aggregate query executes if cohort N < 11.
2. Minimum group size: no grouped result releases if group N < 11.
3. Filter generalization: replace granular filters with approved broader categories
   where safe; otherwise suppress.
4. No arbitrary free-text filters against patient-level datasets.
5. No drill-down from a released group to subgroups unless every resulting and
   inferable subgroup remains non-disclosive.
6. Query history ledger: evaluate overlapping queries by the same user, tenant,
   role, workspace, and defined time window.
7. Deny differencing attempts rather than returning altered counts that disclose
   the sensitive complement.
8. Restrict exports to the same suppression engine; never export pre-suppression data.
```

A query-history ledger is essential. A per-query \(N \geq 11\) check alone does not prevent attacks such as:

```text
All patients with condition X: 100
All patients with condition X excluding patient attribute Y: 90
Derived count for attribute Y: 10   ← prohibited disclosure
```

## 6.5 Safe Harbor identifiers

The aggregate guardrail does not replace Safe Harbor de-identification requirements. Outputs must be scanned and blocked for identifiers, including:
- names;
- geographic subdivisions smaller than a state, subject to permitted ZIP-code rules;
- dates more specific than year, with limited permitted exceptions;
- ages over 89 expressed in a way that identifies an individual;
- telephone, fax, email, SSN, medical-record, account, certificate/license, vehicle, device, URL, IP, biometric, photograph, and other unique identifying numbers or characteristics.

A Copilot must not return patient-level rows in response to analytics questions, even if the total cohort is \(N \geq 11\).

---

# 7. Required endpoint controls

| Endpoint type | Required guardrail |
|---|---|
| `POST /copilot/chat` | Inbound MIR/off-label interception; PHI redaction before nonessential logging; safety-event detection; output Fair Balance check. |
| `POST /copilot/retrieve` | Approved-source allowlist; product and label-version binding; retrieval provenance; prevent uncontrolled document access. |
| `POST /analytics/query` | Query AST allowlist; row-level authorization; \(N \geq 11\), complementary suppression, overlap/differencing analysis before result creation. |
| `POST /exports/*` | Re-run the final disclosure-control engine on exported representation; no bypass by CSV, PDF, chart image, email, or API. |
| `POST /mir` | Minimum necessary intake; consent/privacy notice; strict Commercial–Medical segregation; immutable routing audit event. |
| `POST /admin/rules` | Part 11-controlled change management, approval workflow, effective dates, electronic signatures where applicable, rollback, and immutable audit history. |
| `POST /feedback` | Do not allow user feedback to directly retrain prompts, claims, label mappings, or rules without review and formal release. |

---

# 8. Security and compliance validation checklist

The following checklist should be executed with recorded evidence before production release.

## A. Off-label/MIR firewall

- [ ] A query explicitly containing “off-label,” “not approved,” or “outside the label” is routed to MIR with no substantive answer.
- [ ] A labeled product plus an unapproved disease indication is routed to MIR.
- [ ] A labeled product plus an unapproved dose, schedule, route, combination, disease stage, or population is routed to MIR.
- [ ] A query whose use cannot be confidently mapped to the current PI is routed to MIR, not answered.
- [ ] The same rule applies to paraphrases, misspellings, Unicode-obfuscated text, abbreviations, and multilingual content supported by the application.
- [ ] Prompt injection language does not bypass the firewall.
- [ ] Retrieval, tools, citations, and model draft content are not exposed before the firewall decision.
- [ ] MIR routing records contain rule version, product/label version where resolved, reason code, timestamp, and immutable case linkage.
- [ ] Commercial users cannot access MIR case details beyond permitted operational status.

## B. Fair Balance and promotional claim controls

- [ ] Every benefit statement is linked to an approved claim ID and current label version.
- [ ] Unsupported efficacy, absolute, comparative, superiority, or broad population claims are rejected.
- [ ] Every benefit-containing promotional output includes the required structured risk component.
- [ ] Risk text is visible without clicking, scrolling to a separate asset, opening an accordion, or following a link.
- [ ] Rendered risk text meets size, contrast, placement, and accessibility controls in every supported channel.
- [ ] Email subjects, push notifications, cards, snippets, exports, and previews cannot display benefit claims while omitting the required risk disclosure.
- [ ] Label updates invalidate or re-review linked promotional claims and risk components.
- [ ] Final rendering—not only pre-rendered markdown—is captured in validation evidence.

## C. Privacy and aggregate disclosure controls

- [ ] Cells \(N = 0\) through \(N = 10\) are suppressed in UI, API, charts, tooltips, exports, and generated natural-language summaries.
- [ ] Numerators, denominators, rates, percentages, confidence intervals, and totals cannot disclose suppressed values.
- [ ] Complementary suppression prevents derivation from totals.
- [ ] Sequential, overlapping, and exclusion queries are tested for differencing attacks.
- [ ] Drill-down, pivot, cross-tab, saved query, scheduled report, and export paths use the same disclosure-control engine.
- [ ] Patient-level data and direct identifiers are never returned by the Copilot.
- [ ] Logs, traces, monitoring, and model-evaluation datasets contain redacted/tokenized input only, except where a documented lawful and access-controlled safety workflow requires otherwise.
- [ ] Queries involving dates, geography, age over 89, rare conditions, or rare combinations are generalized or denied where re-identification risk remains.

## D. Part 11 and security controls

- [ ] Rules, PI versions, claim libraries, prompt releases, and routing configurations are versioned and approval-controlled.
- [ ] Audit records are attributable, time-stamped, tamper-evident, retained, and reviewable.
- [ ] Human overrides require authorized identity, reason, timestamp, and review workflow.
- [ ] No administrator can silently modify regex, label mappings, claim content, or suppression thresholds.
- [ ] Access controls enforce least privilege and separation of Commercial, Medical Affairs, Pharmacovigilance, Privacy, and platform-administration roles.
- [ ] Production monitoring alerts on guardrail bypasses, unexpected rule failures, increased MIR routing, suppression failures, and configuration changes.
- [ ] Failures in label lookup, risk-component retrieval, rendering validation, or privacy calculation fail closed.

---

# 9. Audit conclusion

No claim of compliance can be made without reviewing the actual Copilot design and validating the implemented endpoints against the above controls.

The minimum acceptable OPDP Compliance Guardrail is **not** a single regex filter. It must be a fail-closed, version-controlled decision service that:

1. uses regex and entity extraction to identify risk signals;
2. uses an approved-label ontology to decide whether a requested use is on-label;
3. routes all explicit, detected, ambiguous, or unresolved off-label requests to MIR without substantive response;
4. permits promotional benefit content only through approved claim objects bound to current risk components and final-rendered Fair Balance checks; and
5. enforces \(N \geq 11\) suppression, complementary suppression, and differencing protection before any analytic output is generated or exported.