# Q&A Log — Topic 7: Probabilistic Thinking vs Certainty

> Questions you asked during study, with answers. Appended each session.

---

**Q [2026-05-27]:** This sounds good but I need a real-life example of how you would assign this probability. Take a stock like Pokarna — the primary debate is will the US ADD (anti-dumping duty) case go Pokarna's way or not? Imagine yourself as the world's best investment analyst and build the thesis with the probability so I know exactly how this is done.

**A:** *(Teaching example — the method matters, the specific numbers below are illustrative inputs you'd replace with your own research. This is not a buy/sell recommendation on Pokarna.)*

The mistake most people make is starting with "will the case go Pokarna's way — yes or no?" That's binary thinking, the exact trap this topic warns against. A good analyst never assigns a probability to a *verdict*. They decompose the event into **outcomes that map to cash flows**, because intrinsic value only cares about cash.

**Step 1 — Define the outcome space, not the yes/no.** The US DOC sets a duty *rate* (a continuous variable), so you bucket it into scenarios that matter to the business:

| Scenario | ADD rate outcome | Meaning for US quartz exports | Prob (illustrative) |
|---|---|---|---|
| A — Clean win | Low/negligible (<5%) | US economics intact; margins hold | 25% |
| B — Manageable | Moderate (~5–15%) | Partly passed to customers, some margin hit | 35% |
| C — Painful | High (~15–40%) | US channel impaired; must pivot geographies | 30% |
| D — Catastrophic | Punitive (>40%)/retroactive | US quartz business uneconomic | 10% |

Probabilities sum to 100%; scenarios are mutually exclusive and collectively exhaustive. That discipline alone puts you ahead of most participants arguing "win vs lose."

**Step 2 — Attach an intrinsic value to each scenario** (do a rough earnings re-estimate per scenario):

| Scenario | Est. earnings impact | Implied fair value/share (illustrative) | Prob |
|---|---|---|---|
| A | Full earnings power | ₹900 | 25% |
| B | ~85% of earnings power | ₹720 | 35% |
| C | ~50% of earnings power | ₹380 | 30% |
| D | US ~zero; only apparel+domestic | ₹180 | 10% |

**Step 3 — Expected value = probability-weighted sum:**

> EV = (0.25×900) + (0.35×720) + (0.30×380) + (0.10×180)
> EV = 225 + 252 + 114 + 18 = **₹609**

**Step 4 — Compare EV to the market price.** If the stock is at ₹350, the market is implicitly pricing close to Scenario C as base case, and you have positive edge *if your probabilities are better than the market's*. If it's at ₹650, the market is more optimistic than you and there's no margin of safety even though you're "bullish."

The thesis isn't "the case will go their way." It's: *"the market is pricing a ~70% chance of the painful/catastrophic outcomes; my research says it's closer to 40%, and even in the bad scenarios the downside is ₹180–380 while the upside is ₹720–900. The payoff is asymmetric in my favour."* Probability-weighted, asymmetric, anchored to price — that's a professional-grade thesis.

---

**Q [2026-05-27]:** In practice, would I take different aspects of the business, do case simulation, and come up with a weighted average of all? Is this how it's done?

**A:** Yes — but with a refinement so you don't drown in complexity.

You do **not** simulate every aspect independently and average them. That's false precision and analysis paralysis. Instead:

1. **Identify the one or two variables that actually swing the outcome.** For Pokarna today that's the ADD rate. The new apparel line doesn't move intrinsic value 40%; the duty does. Most "aspects" of a business are noise around one or two swing factors.

2. **Build scenarios around those swing variables** — each scenario is a *coherent world*, not an independent slider. In the "catastrophic duty" world you don't also assume record demand and expanding margins. Variables are correlated, so you model whole scenarios.

3. **Then probability-weight the scenarios** into an expected value.

Why weight *whole scenarios* rather than averaging *individual factors*: factors interact. Averaging each factor separately (average duty × average demand × average margin) produces a blended "mush" case that may correspond to no real future, and it systematically understates tail risk. Real analysts think in discrete, internally-consistent worlds.

For an important position, also run a **pre-mortem** (Topic 6 inversion): "it's two years later and I've lost 50% — what happened?" That surfaces a scenario you underweighted, which you fold back into the table.

So: yes, scenario simulation plus probability weighting — built around the *few* variables that matter, as coherent worlds, not a spreadsheet of every aspect averaged.

---

**Q [2026-05-27]:** How are the weights themselves assigned? Is that simply gut feel? In the Pokarna example there are China-case precedents but one can argue India is different. I'm assuming it's gut feel, because if there were accuracy it would already be priced in.

**A:** Sharpest question of the three, and you've half-answered it yourself. Two parts.

**How weights are assigned — the ladder from base rate to judgement (not pure gut feel):**

1. **Start with the base rate (the outside view).** How have comparable US ADD cases against similar products from other countries resolved? The China quartz precedent is exactly the right instinct. If Chinese quartz got punitive duties in, say, 70% of comparable determinations, your *starting* prior for the bad outcomes anchors near that. Anchoring to the base rate *before your opinion enters* is the single most important discipline here — most people skip straight to their opinion.

2. **Adjust for the specific case (the inside view), justifying each adjustment.** "India is different" — but how much, and why? Is India's cost structure genuinely lower (making a dumping finding harder to sustain)? Is Pokarna's specific historical rate lower than peers? Each factor moves you off the base rate by a *defined* amount: "this takes me from 70% to 55%, because X." If you can't articulate the *why*, you're not allowed the adjustment. That rule separates calibrated judgement from gut feel.

3. **The residual is genuine judgement — but calibrated, not a guess.** After base rate and documented adjustments, an irreducible core is subjective. The professional doesn't remove the subjectivity; theirs is anchored, documented, and therefore *correctable* when new facts arrive.

**"If there's accuracy, it will be priced in" — you've reasoned your way to the efficient market hypothesis and its escape hatch, variant perception.**

You're right: if your probability estimate is just the consensus estimate, it's already in the price and you have no edge. Correctly guessing 40% when the market also thinks 40% earns nothing. Edge comes from three places, none of which is "being smarter at arithmetic":

- **Variant perception (Steinhardt):** your probability differs from the market's *and you can name specifically why the market is wrong* — "the market prices 65% bad outcomes because it's anchoring on the scary China headline and hasn't seen that Pokarna's specific cost structure makes its rate structurally lower. I've done that work; my 40% is better-informed." Edge requires naming *the specific reason the crowd is mispricing.*

- **Time-horizon arbitrage (Topic 3):** even if your probability equals the market's, institutions may be unable to *hold* through 18 months of headline risk. You can. Structural edge independent of probability accuracy.

- **Asymmetry the market ignores:** sometimes you don't need a better probability — you notice the payoff is lopsided (downside ₹180, upside ₹900) while the market treats it as symmetric because binary win/lose framing hides the asymmetry.

So your instinct is correct: if your only claim is "I estimated the probability accurately," you have no edge, because so did everyone. The edge is the **variant** — the specific, defensible reason your probability differs from the price-implied one. Your job isn't to compute the "true" probability; it's to find the gap between the *market's implied probability* and the *defensible probability*, and know exactly why that gap exists. Reframing from "what's the right probability?" to "where and why is the market's implied probability wrong?" is the entire game.

---
