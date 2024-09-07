from common.schemas.aggregated import AggregationSchema
import bittensor as bt


def process_aggregation(
    aggregation: AggregationSchema,
    CTRmax: float,
    Wots: float,
    Wuvps: float,
    Wuv: float,
    Wctr: float,
    UVmax: float,
    ndigits: int = 5,
) -> float:
    """
    Processes aggregation data to calculate a rating based on various parameters.

    Args:
        aggregation (AggregationSchema): Aggregated data schema containing visit and click statistics.
        CTRmax (float): Maximum value for Click-Through Rate (CTR) normalization.
        Wots (float): Weight for Opportunities to See (OTS) in rating calculation.
        Wuvps (float): Weight for Unique Visits per Session (UVPS) in rating calculation.
        Wuv (float): Weight for Unique Visits (UV) in rating calculation.
        Wctr (float): Weight for Click-Through Rate (CTR) in rating calculation.
        UVmax (float): Maximum value for Unique Visits (UV) normalization.
        ndigits (int, optional): Number of digits to round the final rating to. Defaults to 5.

    Returns:
        float: The computed rating for the aggregation data, rounded to `ndigits` decimal places.
    """
    CTR = 0.0
    if aggregation.visits_unique > 0:
        CTR = aggregation.count_through_rate_click / aggregation.visits_unique
    if CTR > 0.2:
        CTR = 0.0

    # Calculate UV (Unique Visits) normalization
    UV = aggregation.visits_unique
    Unorm = UV / UVmax

    # Calculate CTR normalization
    CTRnorm = CTR / CTRmax

    # Calculate OTS (Opportunities to See)
    OTS = 1
    if aggregation.at > 0:
        if aggregation.visits_unique > 0:
            if aggregation.at >= aggregation.visits_unique:
                OTS = 0
            elif aggregation.visits_unique > 0:
                OTS = aggregation.at / aggregation.visits_unique
        else:
            OTS = 0
        OTS = min(OTS, 1)
    if OTS != 1 and OTS != 0:
        OTS = min(1 - OTS, 1)
    RATING = 0

    # Calculate RATING
    if OTS > 0.25:
        UVPS = 0
        if aggregation.visits_unique > 0 and aggregation.visits > 0:
            UVPS = aggregation.visits_unique / aggregation.visits
        ATI = (Wots * OTS) + (Wuvps * UVPS)
        RATING = ((Wuv * Unorm) + (Wctr * CTRnorm)) * ATI

    return round(RATING, ndigits)


def process_cpa(
    aggregation: AggregationSchema,
    MR: float,
    SALESmax: float,
    CRmax: float,
    MRmax: float,
    Wsales: float,
    Wcr: float,
    Wmr: float,
    ndigits: int = 5,
) -> float:
    """
    Processes Cost-Per-Action (CPA) related data to calculate a rating based on sales, conversion rate,
    and miner reputation.

    Args:
        aggregation (AggregationSchema): Aggregated data schema containing sales and visit statistics.
        MR (float): Miner reputation score.
        SALESmax (float): Maximum value for total sales normalization.
        CRmax (float): Maximum value for Conversion Rate (CR) normalization.
        MRmax (float): Maximum value for Miner Reputation (MR) normalization.
        Wsales (float): Weight for sales amount in rating calculation.
        Wcr (float): Weight for Conversion Rate (CR) in rating calculation.
        Wmr (float): Weight for Miner Reputation (MR) in rating calculation.
        ndigits (int, optional): Number of digits to round the final rating to. Defaults to 5.

    Returns:
        float: The computed rating for the CPA data, rounded to `ndigits` decimal places.
    """
    # Calculate Conversion Rate (CR)
    CVR = (
        aggregation.total_sales / aggregation.visits_unique
        if aggregation.visits_unique > 0
        else 0.0
    )

    # Calculate Refunds Percentage (RP) and Refunds Score (RF)
    RP = (
        aggregation.total_refunds / aggregation.total_sales
        if aggregation.total_sales > 0
        else 0.0
    )
    RF = 1.0 if RP < 0.2 else 0.0

    # Normalize the parameters
    SALESnorm = min(aggregation.sales_amount / SALESmax, 1.0)
    CRnorm = min(CVR / CRmax, 1.0)
    MRnorm = min(MR / MRmax, 1.0)

    # Calculate Miner Score
    RATING = ((Wsales * SALESnorm) + (Wcr * CRnorm) + (Wmr * MRnorm)) * RF

    # Ensure the Miner Score is within the range [0, 1] and rounded to 5 decimal places
    RATING = round(min(RATING, 1.0), ndigits)

    # Log all parameters and intermediate values
    bt.logging.debug(
        f"""
    Process CPA - Parameters and Intermediate Values:
    MR: {MR},
    SALESmax: {SALESmax},
    CRmax: {CRmax},
    MRmax: {MRmax},
    Wsales: {Wsales},
    Wcr: {Wcr},
    Wmr: {Wmr},
    ndigits: {ndigits},
    total_sales: {aggregation.total_sales},
    visits_unique: {aggregation.visits_unique},
    total_refunds: {aggregation.total_refunds},
    sales_amount: {aggregation.sales_amount},
    CVR (Conversion Rate): {CVR},
    RP (Refund Percentage): {RP},
    RF (Refund Score): {RF},
    SALESnorm: {SALESnorm},
    CRnorm: {CRnorm},
    MRnorm: {MRnorm},
    Final RATING: {RATING}
    """
    )

    return RATING
