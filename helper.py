def adjusted_amount(amount, token_symbol):
    if token_symbol in ['USDC', 'UST', 'LUNA']:
        return amount / 1e6
    elif token_symbol in ['EURS']:
        return amount / 1e2
    else:
        return amount / 1e18
