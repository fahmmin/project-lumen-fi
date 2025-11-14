"""
PROJECT LUMEN - Investment Calculator Utilities
Calculates investment returns, asset allocation, and savings plans
"""

from typing import Dict, List, Tuple
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class InvestmentCalculator:
    """Investment and savings calculations"""

    @staticmethod
    def calculate_monthly_savings_needed(
        target_amount: float,
        current_savings: float,
        months: int,
        annual_return: float = 0.0
    ) -> float:
        """
        Calculate monthly savings needed to reach goal

        Args:
            target_amount: Target amount to save
            current_savings: Current savings
            months: Number of months to goal
            annual_return: Expected annual return (0.06 = 6%)

        Returns:
            Monthly savings required
        """
        if months <= 0:
            return 0.0

        remaining = target_amount - current_savings

        if annual_return == 0:
            # Simple division if no returns
            return remaining / months

        # Future value of annuity formula
        monthly_rate = annual_return / 12

        # FV = PMT * [((1 + r)^n - 1) / r]
        # Solve for PMT: PMT = FV / [((1 + r)^n - 1) / r]

        if monthly_rate == 0:
            return remaining / months

        numerator = remaining - (current_savings * ((1 + monthly_rate) ** months))
        denominator = ((1 + monthly_rate) ** months - 1) / monthly_rate

        return max(0, numerator / denominator)

    @staticmethod
    def project_future_value(
        current_amount: float,
        monthly_contribution: float,
        months: int,
        annual_return: float
    ) -> float:
        """
        Project future value with monthly contributions

        Args:
            current_amount: Starting amount
            monthly_contribution: Monthly contribution
            months: Number of months
            annual_return: Annual return rate

        Returns:
            Future value
        """
        monthly_rate = annual_return / 12

        # Future value of current amount
        fv_current = current_amount * ((1 + monthly_rate) ** months)

        # Future value of annuity (monthly contributions)
        if monthly_rate == 0:
            fv_contributions = monthly_contribution * months
        else:
            fv_contributions = monthly_contribution * (
                ((1 + monthly_rate) ** months - 1) / monthly_rate
            )

        return fv_current + fv_contributions

    @staticmethod
    def recommend_asset_allocation(
        years_to_goal: float,
        risk_tolerance: str = "moderate"
    ) -> Dict:
        """
        Recommend asset allocation based on time horizon

        Args:
            years_to_goal: Years until goal
            risk_tolerance: "conservative", "moderate", or "aggressive"

        Returns:
            Asset allocation percentages
        """
        # Base allocation on time horizon
        if years_to_goal < 1:
            # Very short term - mostly cash
            base_stocks = 20
            base_bonds = 50
            base_cash = 30
        elif years_to_goal < 3:
            # Short term - conservative
            base_stocks = 40
            base_bonds = 50
            base_cash = 10
        elif years_to_goal < 5:
            # Medium term - moderate
            base_stocks = 60
            base_bonds = 35
            base_cash = 5
        elif years_to_goal < 10:
            # Long term - growth
            base_stocks = 70
            base_bonds = 25
            base_cash = 5
        else:
            # Very long term - aggressive growth
            base_stocks = 80
            base_bonds = 18
            base_cash = 2

        # Adjust for risk tolerance
        if risk_tolerance == "conservative":
            base_stocks = max(0, base_stocks - 20)
            base_bonds = min(100, base_bonds + 15)
            base_cash = min(100, base_cash + 5)
        elif risk_tolerance == "aggressive":
            base_stocks = min(100, base_stocks + 10)
            base_bonds = max(0, base_bonds - 10)

        # Normalize to 100%
        total = base_stocks + base_bonds + base_cash
        stocks = round((base_stocks / total) * 100)
        bonds = round((base_bonds / total) * 100)
        cash = 100 - stocks - bonds

        return {
            "stocks": stocks,
            "bonds": bonds,
            "cash": cash,
            "risk_level": InvestmentCalculator._get_risk_level(stocks)
        }

    @staticmethod
    def _get_risk_level(stock_percentage: int) -> str:
        """Determine risk level from stock percentage"""
        if stock_percentage >= 80:
            return "aggressive"
        elif stock_percentage >= 60:
            return "moderate"
        else:
            return "conservative"

    @staticmethod
    def estimate_expected_return(allocation: Dict) -> float:
        """
        Estimate expected annual return based on allocation

        Args:
            allocation: Asset allocation dict

        Returns:
            Expected annual return (as decimal)
        """
        # Historical average returns (simplified)
        stock_return = 0.10  # 10% historically
        bond_return = 0.05   # 5% historically
        cash_return = 0.02   # 2% historically

        expected_return = (
            (allocation.get("stocks", 0) / 100) * stock_return +
            (allocation.get("bonds", 0) / 100) * bond_return +
            (allocation.get("cash", 0) / 100) * cash_return
        )

        return expected_return

    @staticmethod
    def create_milestones(
        start_date: date,
        target_date: date,
        target_amount: float,
        current_savings: float
    ) -> List[Dict]:
        """
        Create milestone checkpoints for goal

        Args:
            start_date: Start date
            target_date: Goal target date
            target_amount: Target amount
            current_savings: Current savings

        Returns:
            List of milestones
        """
        milestones = []

        # Calculate total months
        months_total = (
            (target_date.year - start_date.year) * 12 +
            (target_date.month - start_date.month)
        )

        if months_total <= 0:
            return milestones

        # Create quarterly milestones for first year, then yearly
        checkpoint_months = []

        if months_total <= 12:
            # Quarterly for first year
            for i in range(3, months_total, 3):
                checkpoint_months.append(i)
        else:
            # Quarterly for first year, then yearly
            checkpoint_months = [3, 6, 9, 12]
            years = months_total // 12
            for year in range(2, years + 1):
                checkpoint_months.append(year * 12)

        # Final milestone
        if months_total not in checkpoint_months:
            checkpoint_months.append(months_total)

        # Generate milestones
        for months in checkpoint_months:
            milestone_date = start_date + relativedelta(months=months)
            progress = months / months_total
            target_savings = current_savings + (target_amount - current_savings) * progress

            milestones.append({
                "date": milestone_date.isoformat(),
                "months_from_start": months,
                "target_amount": round(target_savings, 2),
                "progress_percentage": round(progress * 100, 1),
                "description": f"{months} months - {round(progress * 100, 0)}% complete"
            })

        return milestones

    @staticmethod
    def calculate_interest_savings(
        debt_amount: float,
        interest_rate: float,
        extra_payment: float,
        min_payment: float
    ) -> Dict:
        """
        Calculate interest savings from extra debt payments

        Args:
            debt_amount: Current debt amount
            interest_rate: Annual interest rate (0.15 = 15%)
            extra_payment: Extra payment per month
            min_payment: Minimum payment per month

        Returns:
            Savings analysis
        """
        monthly_rate = interest_rate / 12

        # Calculate payoff with minimum payment
        balance_min = debt_amount
        months_min = 0
        interest_min = 0

        while balance_min > 0 and months_min < 360:  # Cap at 30 years
            interest_charge = balance_min * monthly_rate
            principal = min_payment - interest_charge

            if principal <= 0:
                # Can't pay off with minimum payment
                break

            balance_min -= principal
            interest_min += interest_charge
            months_min += 1

        # Calculate payoff with extra payment
        balance_extra = debt_amount
        months_extra = 0
        interest_extra = 0
        total_payment = min_payment + extra_payment

        while balance_extra > 0 and months_extra < 360:
            interest_charge = balance_extra * monthly_rate
            principal = total_payment - interest_charge
            balance_extra -= principal
            interest_extra += interest_charge
            months_extra += 1

        return {
            "debt_amount": debt_amount,
            "min_payment_plan": {
                "months": months_min,
                "total_interest": round(interest_min, 2)
            },
            "accelerated_plan": {
                "months": months_extra,
                "total_interest": round(interest_extra, 2),
                "extra_monthly": extra_payment
            },
            "savings": {
                "interest_saved": round(interest_min - interest_extra, 2),
                "months_saved": months_min - months_extra
            }
        }
