# Apollo and Crunchbase filter sets — copy ready

Apply the **global exclusions to every search**. Cold sends on Apollo cousin
domains only, never silverside.ai primary. Human-in-the-loop approval before
any send. Verify every email address before enrolment.

## Global exclusions (every search)

```
EXCLUDE Industry: Banking, Financial Services (institutional), Insurance,
  Hospital & Health Care (providers), Pharmaceuticals (Rx), Government
  Administration, Legal Services, Accounting, Real Estate, Construction,
  Oil & Energy, Mining & Metals, Wholesale, Staffing & Recruiting,
  Higher Education, Cryptocurrency
EXCLUDE Employee count: 1-50
EXCLUDE Revenue: under $100M
EXCLUDE Country: Germany, France, Canada   [pending legal review: GDPR / CASL]
EXCLUDE existing Silverside clients and active pipeline  [data/suppression_list.csv]
EXCLUDE job function: Legal, Finance, Human Resources, Information Security
REQUIRE Email status: Verified
```

## Set A — CPG multi brand

```
Industry: Food & Beverages, Consumer Goods, Consumer Products,
  Wine & Spirits, Packaging & Containers
Revenue: $250M - $10B        Employees: 500 - 10,000
Country: United States, United Kingdom
Keywords (company): "brands" OR "portfolio" OR "brand family"
Technologies: Salsify OR Syndigo OR Adobe Experience Manager OR Bynder
Titles: "Creative Operations" OR "Marketing Operations" OR "VP Brand" OR
  "Head of Brand" OR "Brand Marketing" OR "Integrated Marketing" OR
  "Shopper Marketing" OR "Trade Marketing" OR "Global Marketing" OR
  "Head of Content" OR "Chief Marketing Officer"
Seniority: Director, VP, Head, C-Suite      Contacts per account: 4
```

## Set B — Omnichannel retail and mass merchant

```
Industry: Retail, Apparel & Fashion, Supermarkets, Consumer Electronics,
  Furniture, Sporting Goods
Revenue: $500M - $20B        Employees: 1,000 - 50,000
Country: United States, United Kingdom
Keywords (company): "retail media" OR "stores" OR "omnichannel" OR "marketplace"
Technologies: Salesforce Commerce Cloud OR SAP Commerce OR Salsify OR
  Adobe Experience Manager OR Shopify Plus
Titles: "Retail Media" OR "VP E-commerce" OR "Head of E-commerce" OR
  "Creative Operations" OR "Digital Content" OR "VP Digital" OR
  "Marketing Operations" OR "VP Brand Marketing"
Seniority: Director, VP, Head, C-Suite      Contacts per account: 5
```

## Set C — Beauty, cosmetics, personal care

```
Industry: Cosmetics, Personal Care & Consumer Products,
  Health Wellness & Fitness, Retail (beauty subcategory)
Revenue: $250M - $5B         Employees: 200 - 5,000
Country: United States, United Kingdom
Keywords (company): "beauty" OR "cosmetics" OR "skincare" OR "fragrance" OR
  "personal care"
Titles: "VP Brand" OR "Head of Brand" OR "VP Digital" OR "Head of Content" OR
  "Creative Operations" OR "VP E-commerce" OR "Global Marketing" OR
  "Head of Social" OR "Chief Marketing Officer"
Seniority: Director, VP, Head, C-Suite      Contacts per account: 4
```

## Set D — Fashion, apparel, footwear, accessories

```
Industry: Apparel & Fashion, Retail, Luxury Goods & Jewelry, Textiles,
  Sporting Goods
Revenue: $250M - $5B         Employees: 200 - 10,000
Country: United States, United Kingdom
Technologies: Shopify Plus OR Salesforce Commerce Cloud OR Bynder OR
  Adobe Experience Manager OR Frame.io
Titles: "VP E-commerce" OR "Head of E-commerce" OR "Creative Operations" OR
  "Studio Director" OR "Head of Studio" OR "VP Brand" OR "Head of Content" OR
  "VP Digital" OR "Creative Director"
Seniority: Director, VP, Head, C-Suite      Contacts per account: 4
```

## Set E — QSR, fast casual, restaurants, franchise

```
Industry: Restaurants, Food & Beverages, Hospitality, Consumer Services
Revenue: $250M - $5B   [or system sales where reported]
Employees: 500 - 50,000      Country: United States
Keywords (company): "franchise" OR "franchisee" OR "locations" OR
  "restaurants" OR "quick service"
Titles: "Field Marketing" OR "Franchise Marketing" OR "Local Marketing" OR
  "VP Marketing" OR "VP Brand" OR "Chief Marketing Officer" OR
  "Creative Operations" OR "Head of Creative" OR "Regional Marketing"
Seniority: Director, VP, Head, C-Suite      Contacts per account: 4
```

## Set F — AI transformation, cross vertical  [HIGHEST REPLY RATE]

```
Industry: [all Tier 1 and Tier 2 industries]
Revenue: $250M+
Titles: "Generative AI" OR "Head of AI" OR "Chief AI Officer" OR
  "Director of AI" OR "AI Product" OR "AI Program" OR "Innovation" OR
  "Emerging Technology" OR "Digital Transformation"
AND department contains: Marketing OR Brand OR Creative OR Digital
Seniority: Director, VP, Head, C-Suite
Contacts per account: 3, plus 2 from the marketing budget layer
```

Highest expected reply rate of any filter set in the model. **Overweight
this.** Send technical depth, not a deck. This persona rarely holds budget,
so always identify their economic buyer on call one.

## Set G — Recently funded (Crunchbase then Apollo)

```
CRUNCHBASE:
  Last funding amount: $20M+          Last funding date: trailing 18 months
  Funding stage: Series B, C, D, E, Growth
  Industry: Consumer Goods, E-commerce, Food & Beverage, Beauty, Apparel,
    Consumer Health, Software (consumer facing only)
  Headquarters: United States, United Kingdom      Employee count: 50+
  EXCLUDE: Crypto, Blockchain, Cannabis, Gambling, Defense

APOLLO, on the resulting company list:
  Titles: "Chief Marketing Officer" OR "VP Marketing" OR "Head of Brand" OR
    "Head of Content" OR "VP Growth" OR "Head of Creative"
  Contacts per account: 2
  CAP TOTAL AT 15 PERCENT OF ACTIVE COLD VOLUME
```

## Set H — PE portfolio consumer (dual track)

```
CRUNCHBASE or PITCHBOOK:
  Ownership: Private Equity backed    Acquisition date: trailing 24 months
  Industry: Consumer, Retail, Food & Beverage, Beauty, Apparel,
    Restaurants, Consumer Health
  Revenue: $100M - $2B

APOLLO, portfolio company direct:
  Titles: "Chief Marketing Officer" OR "VP Marketing" OR "VP Brand" OR
    "Chief Financial Officer" OR "Creative Operations"
  Contacts per account: 3

PARALLEL SPONSOR MOTION  [higher leverage path]:
  Target consumer focused PE firms at operating partner level.
  Titles: "Operating Partner" OR "Operating Executive" OR
    "Head of Value Creation" OR "Portfolio Operations"
  One sponsor relationship can produce 4 to 8 portfolio conversations.
```

## Master target account definition

```
Industry: Retail, Consumer Goods, Food & Beverages, Apparel & Fashion,
  Cosmetics, Restaurants, Wine & Spirits, Consumer Electronics, Hospitality,
  Health & Wellness, Sporting Goods, Furniture, Luxury Goods
Revenue: $250M - $10B        Employees: 200 - 10,000
Country: United States, United Kingdom
Requires at least ONE of:
  3+ brands  |  500+ SKUs  |  100+ locations  |  5+ markets or languages
Requires: 50+ active creatives in Meta Ad Library
Plus all global exclusions above.
```

## Master target contact definition

```
Titles containing: "Creative Operations" | "Marketing Operations" |
  "Content Operations" | "Studio" | "Production" | "VP Brand" |
  "Head of Brand" | "Brand Marketing" | "Integrated Marketing" |
  "Global Marketing" | "VP E-commerce" | "Head of E-commerce" |
  "Retail Media" | "VP Digital" | "Performance Marketing" |
  "Generative AI" | "Head of AI" | "Innovation" | "Emerging Technology" |
  "Field Marketing" | "Franchise Marketing" | "Shopper Marketing" |
  "Chief Marketing Officer" | "Chief Brand Officer" | "Chief Digital Officer"
Seniority: Director, Head, VP, SVP, C-Suite
Department: Marketing, Creative, E-commerce, Digital, Innovation
EXCLUDE department: Legal, Finance, Human Resources, Information Security,
  Engineering, Sales
Email status: Verified only
Contacts per account: 2 for Tier 3, 4 to 6 for Tier 2, 5 to 8 for Tier 1
```
