import random

class ForecastRule:
    def __init__(self, rule_string, a, b, sigma_sq, accuracy):
        self.rule_string = rule_string
        self.a = a
        self.b = b
        self.sigma_sq = sigma_sq
        self.accuracy = accuracy
        n_active_bits = 0
        for idx, bit in enumerate(self.rule_string):
            if bit != "#": n_active_bits += 1
        self.strength = -(accuracy + 0.005 * n_active_bits)

    def __str__(self):
        return "Rule: {}, a: {}, b: {}, sig_sq: {}, acc: {}, strg: {}".format(self.rule_string,
                                                                              str(round(self.a, 2)), str(round(self.b, 2)),
                                                                              str(round(self.sigma_sq, 2)),
                                                                              str(round(self.accuracy, 2)),
                                                                              str(round(self.strength, 2)))

    def __repr__(self):
        return str(self)

    def match_to_market(self, stock):
        for idx, ch in enumerate(self.rule_string):
            if ch != "#" and ch != stock.rule_string[idx]: return False
        return True

    def evaluate(self):
        pass


class RuleBook:
    def __init__(self, n_rules=100):
        self.n_rules = n_rules
        self.rules = [generate_random_rule() for i in range(n_rules)]

    def drop_weakest_rules(self, perc=20):
        from numpy import percentile
        strength_threshold = percentile([rule.strength for rule in self.rules], perc)
        self.rules = [x for x in self.rules if x.strength > strength_threshold]

    def add_rule(self, rule):
        self.rules.append(rule)

    def evolve(self, evolution_rate=0.2, crossover_p=0.1):
        [rule.evaluate() for rule in self.rules]  # maybe evaluate in agent at each step
        n_new = int(evolution_rate * self.n_rules)
        self.drop_weakest_rules(n_new)
        for i in range(n_new):
            if random.random() < crossover_p:
                cross_rules = random.choices(self.rules, k=2)
                rule_1, rule_2 = cross_rules[0], cross_rules[1]
                self.add_rule(crossover_rules(rule_1, rule_2))
            else:
                self.add_rule(mutate_rule(random.choice(self.rules)))


def generate_random_rule(str_len=12, p_0=0.05, p_1=0.05, a_low=0.7, a_upp=1.2,
                         b_low=-10., b_upp=19., init_sig=4.):
    string = ""
    for c in range(str_len - 2):
        r = random.random()
        string += "0" if r < p_0 else ("1" if r < p_0 + p_1 else "#")
    string += "10"
    a_mult = a_upp - a_low
    a = random.random() * a_mult + a_low
    b_mult = b_upp - b_low
    b = random.random() * b_mult + b_low
    sigma_sq = init_sig
    accuracy = init_sig
    return ForecastRule(string, a, b, sigma_sq, accuracy)


def crossover_rules(rule_1, rule_2, p_wght_reals=1. / 3., p_picking_reals=1. / 3., p_rule_1=0.5):
    new_string = ""
    for bit_1, bit_2 in zip(rule_1.rule_string, rule_2.rule_string):
        if random.random() < 0.5:
            new_string += bit_1
        else:
            new_string += bit_2

    a_b_sig_p = random.random()
    if a_b_sig_p < p_wght_reals:
        p_1 = rule_1.accuracy / (rule_1.accuracy + rule_2.accuracy)
        p_2 = 1 - p_1
        a = p_1 * rule_1.a + p_2 * rule_2.a
        b = p_1 * rule_1.b + p_2 * rule_2.b
        sigma_sq = p_1 * rule_1.sigma_sq + p_2 * rule_2.sigma_sq
        accuracy = p_1 * rule_1.accuracy + p_2 * rule_2.accuracy

    elif a_b_sig_p < p_wght_reals + p_picking_reals:
        if random.random() < p_rule_1:
            a = rule_1.a
        else:
            a = rule_2.a
        if random.random() < p_rule_1:
            b = rule_1.b
        else:
            b = rule_2.b
        if random.random() < p_rule_1:
            sigma_sq = rule_1.sigma_sq
        else:
            sigma_sq = rule_2.sigma_sq
        if random.random() < p_rule_1:
            accuracy = rule_1.accuracy
        else:
            accuracy = rule_2.accuracy

    else:
        if random.random() < p_rule_1:
            a, b, sigma_sq, accuracy = rule_1.a, rule_1.b, rule_1.sigma_sq, rule_1.accuracy
        else:
            a, b, sigma_sq, accuracy = rule_2.a, rule_2.b, rule_2.sigma_sq, rule_2.accuracy

    return ForecastRule(new_string, a, b, sigma_sq, accuracy)


def mutate_rule(rule, p_bit_mut=0.03, p_0_to_hash=2. / 3., p_1_to_hash=2. / 3., p_hash_to_1=0.5):
    new_rule = rule
    new_string = ""
    for idx, bit in enumerate(new_rule.rule_string):
        if random.random() < p_bit_mut:
            if bit == "0":
                new_string += "#" if random.random() < p_0_to_hash else "1"
            elif bit == "1":
                new_string += "#" if random.random() < p_1_to_hash else "0"
            else:
                new_string += "1" if random.random() < p_hash_to_1 else "0"
        else:
            new_string += bit
    new_rule.rule_string = new_string
    p_a = random.random()
    if p_a < 0.2:
        new_rule.a = random.random() * 0.5 + 0.7  # range from 0.7 to 1.2
    elif p_a < 0.4:
        new_rule.a += ((random.random() - 0.5) / 10) * 0.5

    p_b = random.random()
    if p_b < 0.2:
        new_rule.b = random.random() * 29. - 10.
    elif p_b < 0.4:
        new_rule.b += ((random.random() - 0.5) / 10) * 29

    return new_rule


# rule_1 = generate_random_rule()
# rule_2 = generate_random_rule()
# print(rule_1)
# print(rule_2)
# [print(crossover_rules(rule_1, rule_2)) for i in range(10)]

# rule_book = RuleBook(10)
# [print(rule) for rule in rule_book.rules]
# rule_book.evolve(0.5, 0.5)
# [print(rule) for rule in rule_book.rules]
