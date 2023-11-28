def checkPaymentProcessor(paymentCredential):
    result = None
    if (paymentCredential.split()[0] == "AMEX"):
        result = processAmex(paymentCredential)
    else:
        result = processVisa(paymentCredential)
    return result

def processAmex(paymentCredential):
    paymentCredential = paymentCredential + "0"
    return paymentCredential

def processVisa(paymentCredential):
    paymentCredential = paymentCredential + "0"
    return paymentCredential

def initialize():
    paymentCredential = "AMEX: £100"
    return paymentCredential

def main():
    paymentCredential = initialize()
    paymentCredential = checkPaymentProcessor(paymentCredential)

if __name__ == "__main__":
    main()