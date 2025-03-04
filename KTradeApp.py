import streamlit as st

def main():
    st.title("K Trade Calculator")
    st.write("Calculate trade outcomes with multiple take profit levels, accounting for fees and PnL.")

    with st.form("trade_calculator_form"):
        st.subheader("Trade Parameters")
        entry_price = st.number_input("Enter your entry price:", min_value=0.01, value=10.0, step=0.01)
        sl_price = st.number_input("Enter your stop loss price:", min_value=0.01, value=9.0, step=0.01)
        capital = st.number_input("Enter your total capital ($):", min_value=0.01, value=1000.0, step=1.0)
        fee_percentage = st.number_input("Enter the fee percentage (%):", min_value=0.0, value=0.1, step=0.1)
        num_tp_levels = st.number_input("Enter the number of take profit (TP) levels:", min_value=1, value=1, step=1)
        
        # Convert fee percentage to decimal
        fee = fee_percentage / 100

        # Calculate maximum number of shares available given the entry price and fees.
        max_shares_float = capital / (entry_price * (1 + fee))
        max_shares = int(max_shares_float)
        st.write(f"**Maximum shares you can purchase:** {max_shares}")

        st.subheader("Take Profit Levels")
        tp_levels = []
        shares_allocated = 0

        # Dynamically generate input fields for each TP level.
        for i in range(int(num_tp_levels)):
            st.markdown(f"**TP Level {i + 1}**")
            tp_price = st.number_input(f"Enter price for TP {i + 1}:", min_value=0.0, value=entry_price * 1.1, step=0.01, key=f"tp_price_{i}")
            if i == int(num_tp_levels) - 1:
                remaining_shares = max_shares - shares_allocated
                st.write(f"Automatically allocating remaining {remaining_shares} shares to this level.")
                tp_shares = remaining_shares
            else:
                remaining_shares = max_shares - shares_allocated
                tp_shares = st.number_input(
                    f"Enter number of shares for TP {i + 1} (max {remaining_shares}):",
                    min_value=1,
                    max_value=remaining_shares,
                    value=1,
                    step=1,
                    key=f"tp_shares_{i}"
                )
            shares_allocated += tp_shares
            tp_levels.append({"price": tp_price, "shares": tp_shares})
            st.write(f"Shares allocated so far: {shares_allocated} / {max_shares}")
        
        submitted = st.form_submit_button("Calculate Trade Outcome")
    
    if submitted:
        st.header("Trade Analysis")
        actual_cost = max_shares * entry_price
        entry_fee = actual_cost * fee
        total_entry_cost = actual_cost + entry_fee
        remaining_capital = capital - total_entry_cost
        
        st.write(f"**Initial Capital:** ${capital:.2f}")
        st.write(f"**Entry Price:** ${entry_price:.2f} per share")
        st.write(f"**Number of Shares:** {max_shares}")
        st.write(f"**Entry Cost:** ${actual_cost:.2f} + ${entry_fee:.2f} fee = ${total_entry_cost:.2f}")
        st.write(f"**Remaining Capital:** ${remaining_capital:.2f}")
        
        st.header("Take Profit Scenarios")
        tp_results = []
        total_exit_value = 0
        total_exit_cost = 0

        for i, tp in enumerate(tp_levels):
            tp_price = tp["price"]
            tp_shares = tp["shares"]

            # Calculate exit value and fees
            exit_value = tp_shares * tp_price
            exit_fee = exit_value * fee
            net_exit_value = exit_value - exit_fee

            # Calculate entry cost for these shares
            tp_entry_cost = tp_shares * entry_price
            tp_entry_fee = tp_entry_cost * fee
            tp_total_entry_cost = tp_entry_cost + tp_entry_fee

            # Profit/Loss calculation
            tp_profit = net_exit_value - tp_total_entry_cost
            tp_profit_percentage = (tp_profit / tp_total_entry_cost) * 100
            capital_percentage = (tp_profit / capital) * 100

            tp_results.append({
                "level": i + 1,
                "price": tp_price,
                "shares": tp_shares,
                "profit": tp_profit,
                "profit_percentage": tp_profit_percentage,
                "capital_percentage": capital_percentage
            })

            total_exit_value += net_exit_value
            total_exit_cost += tp_total_entry_cost

            st.markdown(f"**TP {i + 1} (Price: ${tp_price:.2f}, Shares: {tp_shares}):**")
            st.write(f"Exit Value: ${exit_value:.2f} - ${exit_fee:.2f} fee = ${net_exit_value:.2f}")
            st.write(f"Entry Cost for these shares: ${tp_entry_cost:.2f} + ${tp_entry_fee:.2f} fee = ${tp_total_entry_cost:.2f}")
            st.write(f"Profit/Loss: ${tp_profit:.2f} "
                     f"({tp_profit_percentage:.2f}% of position, {capital_percentage:.2f}% of capital)")
        
        overall_profit = total_exit_value - total_exit_cost
        overall_profit_percentage = (overall_profit / total_exit_cost) * 100
        overall_capital_percentage = (overall_profit / capital) * 100
        
        st.header("Overall Take Profit Result")
        st.write(f"**Total Profit (all levels):** ${overall_profit:.2f}")
        st.write(f"**Percentage of Position:** {overall_profit_percentage:.2f}%")
        st.write(f"**Percentage of Capital:** {overall_capital_percentage:.2f}%")
        st.write(f"**Capital After All TPs:** ${capital + overall_profit:.2f}")
        
        st.header("Stop Loss Scenario")
        sl_value = max_shares * sl_price
        sl_fee = sl_value * fee
        net_sl_value = sl_value - sl_fee

        sl_loss = net_sl_value - total_entry_cost
        sl_loss_percentage = (sl_loss / total_entry_cost) * 100
        sl_capital_percentage = (sl_loss / capital) * 100
        
        st.write(f"Stop Loss Scenario (Price: ${sl_price:.2f} × {max_shares} shares):")
        st.write(f"Exit Value: ${sl_value:.2f} - ${sl_fee:.2f} fee = ${net_sl_value:.2f}")
        st.write(f"Loss: ${sl_loss:.2f}")
        st.write(f"Percentage of Position: {sl_loss_percentage:.2f}%")
        st.write(f"Percentage of Capital: {sl_capital_percentage:.2f}%")
        st.write(f"Capital After SL: ${capital + sl_loss:.2f}")
        
        st.header("Risk/Reward Analysis")
        risk = abs(sl_loss)
        reward = overall_profit
        rr_ratio = reward / risk if risk > 0 else float('inf')
        
        st.write(f"Risk: ${risk:.2f} ({abs(sl_capital_percentage):.2f}% of capital)")
        st.write(f"Reward: ${reward:.2f} ({overall_capital_percentage:.2f}% of capital)")
        st.write(f"Risk/Reward Ratio: 1:{rr_ratio:.2f}")

if __name__ == "__main__":
    main()
