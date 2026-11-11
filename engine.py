"""Deterministic, explainable opportunity rules. No external APIs or fabricated market data."""
RULES = [
 ("reviews", "Increase review generation", "reputation", "review_count", lambda v: v < 30, 4, 1, 1, "Ask recent satisfied customers for honest reviews, without incentives or review gating", "New authentic reviews"),
 ("conversion", "Improve lead response and conversion", "conversion", "lead_conversion_rate", lambda v: v < .35, 5, 2, 1, "Audit inquiry response time and create a follow-up script", "Lead-to-customer conversion rate"),
 ("retention", "Reactivate existing customers", "retention", "repeat_customer_rate", lambda v: v < .30, 5, 2, 1, "Prepare an opt-in compliant reactivation campaign for eligible past customers", "Repeat customer rate"),
 ("booking", "Enable frictionless booking", "conversion", "online_booking", lambda v: v is False, 4, 2, 2, "Design an appointment request workflow with owner approval", "Completed bookings"),
 ("referrals", "Create a measurable referral process", "referrals", "referral_tracking", lambda v: v is False, 4, 1, 1, "Prepare a referral invitation and tracking process", "Referred customers"),
 ("profile", "Establish local search presence", "discovery", "google_business_profile", lambda v: v is False, 5, 2, 1, "Claim or optimize the Google Business Profile", "Profile views and calls"),
 ("capacity", "Fill unused service capacity", "acquisition", "capacity_utilization", lambda v: v < .75, 4, 2, 2, "Design a limited, capacity-aware local offer", "Utilization and incremental gross profit"),
]
def opportunities(business):
    metrics = business.get("metrics", {})
    items=[]
    for ident,title,category,field,predicate,impact,effort,cost,action,kpi in RULES:
        if field not in metrics or metrics[field] is None:
            continue
        value=metrics[field]
        if isinstance(value,(int,float,bool)) and predicate(value):
            confidence = .75 if not business.get("demo") else .55
            score = round((impact*3 + confidence*5 - effort - cost),2)
            items.append({"id":ident,"title":title,"category":category,"evidence":{"field":field,"value":value,"source":"demo" if business.get("demo") else "owner_supplied"},"impact_1_to_5":impact,"effort_1_to_5":effort,"cost_1_to_5":cost,"confidence":confidence,"priority_score":score,"recommended_action":action,"primary_kpi":kpi,"impact_estimate":"Not estimated; requires baseline and experiment"})
    return sorted(items,key=lambda x:(-x["priority_score"],x["id"]))
def diagnosis(business):
    metrics=business.get("metrics",{})
    required=["monthly_leads","lead_conversion_rate","repeat_customer_rate","review_count","average_rating","monthly_marketing_budget","capacity_utilization","customer_contacts","online_booking","google_business_profile","referral_tracking"]
    missing=[x for x in required if x not in metrics or metrics[x] is None]
    items=opportunities(business)
    return {"business_id":business["business_id"],"data_source":"demo" if business.get("demo") else "owner_supplied","observed_metrics":metrics,"data_completeness":round((len(required)-len(missing))/len(required),2),"missing_fields":missing,"identified_gaps":[{"category":x["category"],"finding":x["title"],"evidence":x["evidence"]} for x in items],"limitations":["No live competitor, search, advertising or website audit performed","Rules are heuristic, not predictions","No incremental revenue attribution available"]}
def plan(business):
    items = opportunities(business)[:5]
    phases = []
    for start, end, goal in [(1,7,"Validate baseline and prepare"),(8,14,"Launch approved experiments"),(15,21,"Measure and refine"),(22,30,"Review next cycle")]:
        if start == 1:
            activities = [{"opportunity_id":x["id"],"task":x["recommended_action"],"kpi":x["primary_kpi"]} for x in items]
        elif start == 8:
            activities = [{"task":"Run only individually approved actions; record baseline and costs"}]
        elif start == 15:
            activities = [{"task":"Compare KPIs against baseline; flag missing attribution"}]
        else:
            activities = [{"task":"Document outcomes and prioritize next experiments"}]
        phases.append({"days":f"{start}-{end}","goal":goal,"activities":activities})
    return {"business_id":business["business_id"],"duration_days":30,"status":"proposed","phases":phases,"assumptions":["Owner confirms capacity, budget, audience permissions and business priorities","No actions are published automatically"],"opportunity_count":len(items)}
