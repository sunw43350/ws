import pickle


exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

for ex, syms in exchange_symbols.items():
    print(ex, len(syms))