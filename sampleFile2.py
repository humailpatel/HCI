def checkPaymentProcessor(paymentCredential):
    print(f"Entering checkPaymentProcessor with {paymentCredential}")
    result = None
    if (paymentCredential.split()[0] == "AMEX"):
        result = processAmex(paymentCredential)
    else:
        result = processVisa(paymentCredential)
    print(f"Exiting checkPaymentProcessor with {result}")
    return result

def processAmex(paymentCredential):
    print(f"Entering processAmex with {paymentCredential}")
    paymentCredential = paymentCredential + "0"
    print(f"Exiting processAmex with {paymentCredential}")
    return paymentCredential

def processVisa(paymentCredential):
    print(f"Entering processVisa with {paymentCredential}")
    paymentCredential = paymentCredential + "0"
    print(f"Exiting processVisa with {paymentCredential}")
    return paymentCredential

def initialize():
    print("Entering initialize")
    paymentCredential = "AMEX: £100"
    print(f"Exiting initialize with {paymentCredential}")
    return paymentCredential

def main():
    print("Entering main")
    paymentCredential = initialize()
    paymentCredential = checkPaymentProcessor(paymentCredential)
    print(f"Final value in main: {paymentCredential}")

if __name__ == "__main__":
    main()