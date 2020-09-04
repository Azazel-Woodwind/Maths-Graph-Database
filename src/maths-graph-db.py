from neo4j import GraphDatabase


class App:

    def __init__(self, uri, user, pw):
        self.driver = GraphDatabase.driver(uri, auth = (user, pw))
        self.classes = {"M": "A_level_maths", "CP": "FM_core_pure", "FP1": "FM_further_pure_1",
                        "FP2": "FM_further_pure_2",
                        "FS1": "FM_further_stats_1", "FS2": "FM_further_stats_2", "D1": "FM_decision_maths_1",
                        "D2": "FM_decision_maths_2", "Uni": "Cambridge_compsci"}

    def close(self):
        self.driver.close()

    def delete_all(self):
        with self.driver.session() as session:
            session.write_transaction(self._delete_all)
        print("All nodes and relationships deleted")

    @staticmethod
    def _delete_all(tx):
        query = (
            "MATCH (n) DETACH DELETE n"
        )

        tx.run(query)

    def return_all(self):
        with self.driver.session() as session:
            result = session.write_transaction(self._return_all)
        for name in result:
            print(name)

    @staticmethod
    def _return_all(tx):
        query = (
            "MATCH (n) RETURN n"
        )

        result = tx.run(query)

        return [row["n"]["name"] for row in result]

    def create_topic(self, name):
        with self.driver.session() as session:
            session.write_transaction(self._create_topic, name)
        print("Topic created")

    @staticmethod
    def _create_topic(tx, name):
        query = (
            "CREATE (:Topic { name: $name })"
        )

        tx.run(query, name = name)

    def create_relationships_to_one(self, *args):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_relationships_to_one, args)

        for row in result:
            if row[2]:
                print(f"Relationship created between {row[0]} and {row[1]}")
            else:
                print(f"Relationship unable to be created between {row[0]} and {row[1]}")

    @staticmethod
    def _create_relationships_to_one(tx, names):
        query = (
            "MATCH (n1) WHERE n1.name = $start "
            "MATCH (n2) WHERE n2.name = $name "
            "CREATE (n2)-[:RELATED_TO]->(n1) "
            "RETURN n1, n2"
        )

        results = []

        for name in range(1, len(names)):
            result = tx.run(query, start = names[0], name = names[name])
            found = False
            for _ in result:
                found = True
            results.append((names[0], names[name], found))

        return results

    def create_relationships_to_many(self, *args):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_relationships_to_many, args)

        for row in result:
            if row[2]:
                print(f"Relationship created between {row[0]} and {row[1]}")
            else:
                print(f"Relationship unable to be created between {row[0]} and {row[1]}")

    @staticmethod
    def _create_relationships_to_many(tx, names):
        query = (
            "MATCH (n1) WHERE n1.name = $start "
            "MATCH (n2) WHERE n2.name = $name "
            "CREATE (n1)-[:RELATED_TO]->(n2) "
            "RETURN n1, n2"
        )

        results = []

        for name in range(1, len(names)):
            result = tx.run(query, start = names[0], name = names[name])
            found = False
            for _ in result:
                found = True
            results.append((names[0], names[name], found))

        return results

    def create_relationships_consecutively(self, *args):
        with self.driver.session() as session:
            result = session.write_transaction(self._create_relationships_consecutively, args)

        for i in result:
            if i[2]:
                print(f"Relationship created between {i[0]} and {i[1]}")
            else:
                print(f"Relationship unable to be created between {i[0]} and {i[1]}")

    @staticmethod
    def _create_relationships_consecutively(tx, names):
        query = (
            "MATCH (n1) WHERE n1.name = $name1 "
            "MATCH (n2) WHERE n2.name = $name2 "
            "CREATE (n1)-[:RELATED_TO]->(n2) "
            "RETURN n1, n2"
        )

        results = []

        for i in range(len(names) - 1):
            result = tx.run(query, name1 = names[i], name2 = names[i + 1])
            found = False
            for _ in result:
                found = True
            results.append((names[i], names[i + 1], found))

        return results

    def link_sub_topics_to_one(self, *args, **kwargs):
        with self.driver.session() as session:
            session.write_transaction(self._link_sub_topics_to_one, args, kwargs["cls"])

        print("Topics linked")

    def _link_sub_topics_to_one(self, tx, topics, cls):
        query = (
                "MATCH (t1) WHERE t1.name = $start "
                "CREATE (t1)-[:RELATED_TO]->(t2:" + self.classes[cls] + " { name: $topic }) "
        )

        for topic in topics:
            if topic != topics[0]:
                tx.run(query, start = topics[0], topic = topic)

    def link_sub_topics_consecutively(self, *args, **kwargs):
        with self.driver.session() as session:
            session.write_transaction(self._link_sub_topics_consecutively, args, kwargs["cls"])

        print("Topics linked")

    def _link_sub_topics_consecutively(self, tx, path, cls):
        query = (
                "MATCH (t1) WHERE t1.name = $start "
                "CREATE (t1)-[:RELATED_TO]->(t2:" + self.classes[cls] + " { name: $topic }) "
        )

        for name in range(len(path) - 1):
            tx.run(query, start = path[name], topic = path[name + 1])

    def rename_node(self, name, new_name, cls):
        with self.driver.session() as session:
            session.write_transaction(self._rename_node, name, new_name, cls)

        print(f"{name} renamed to {new_name}")

    def _rename_node(self, tx, name, new_name, cls):
        query = (
                "MATCH (n:" + self.classes[cls] + ") WHERE n.name = $name "
                                                  "SET n.name = $new_name"
        )

        tx.run(query, name = name, new_name = new_name)


def create_probability_uni():
    app.create_topic("Probability/Cambridge_compsci")
    app.link_sub_topics_to_one("Probability/Cambridge_compsci", "Counting/Combinatorics", "Probability space", "Axioms",
                               "Union bound", "Conditional probability", "Discrete random variables",
                               "Moments and Limit Theorems", "Statistics", cls = "Uni")
    app.link_sub_topics_consecutively("Conditional probability", "Independence", "Bayes' Theorem", "Partition Theorem",
                                      cls = "Uni")
    app.link_sub_topics_to_one("Discrete random variables", "Random variables", "Probability distributions",
                               "Multivariate distributions", cls = "Uni")
    app.link_sub_topics_consecutively("Random variables", "Definition", "Probability mass function",
                                      "Cumulative distribution", "Expectation", cls = "Uni")
    app.link_sub_topics_consecutively("Probability distributions", "Definition and properties of expectation",
                                      "Variance", "Ways of computing", "Important distributions",
                                      "Continuous distributions",
                                      "Normal and exponential distributions", cls = "Uni")
    app.link_sub_topics_to_one("Important distributions", "Bernoulli", "Binomial", "Geometric", "Poisson", cls = "Uni")
    app.link_sub_topics_consecutively("Multivariate distributions", "Multiple random variables",
                                      "Joint and marginal distributions", "Independence of random variables",
                                      "Covariance", cls = "Uni")
    app.link_sub_topics_to_one("Moments and Limit Theorems", "Law of average", "Markov and Chebyshef inequalities",
                               "Weak Law of Large Numbers", "Moments and Central Limit Theorem", cls = "Uni")
    app.link_sub_topics_consecutively("Statistics", "Classical Parameter Estimation", "Bias", "Sample mean",
                                      "Sample variance",
                                      "Algorithms", cls = "Uni")
    app.link_sub_topics_to_one("Moments and Central Limit Theorem", "Moments of Random Variables",
                               "Central Limit Theorem",
                               cls = "Uni")


def create_central_limit_theorem_fs1():
    app.create_topic("Central limit theorem")
    app.link_sub_topics_consecutively("Central limit theorem", "The central limit theorem",
                                      "Applying to other distributions",
                                      cls = "FS1")


def create_measures_of_location_and_spread_maths():
    app.create_topic("Measures of location and spread/A_level")
    app.link_sub_topics_to_one("Measures of location and spread/A_level", "Measures of central tendency",
                               "Measures of spread", "Coding", cls = "M")
    app.link_sub_topics_consecutively("Measures of central tendency", "Other measures of location", cls = "M")
    app.link_sub_topics_consecutively("Measures of spread", "Variance and standard deviation", cls = "M")
    app.link_sub_topics_to_one("Other measures of location", "Percentiles", "Quartiles", "Interpolation", cls = "M")
    app.link_sub_topics_to_one("Measures of central tendency", "Mode", "Median", "Mean", cls = "M")


def create_probability_maths():
    app.create_topic("Probability/A_level")
    app.link_sub_topics_to_one("Probability/A_level", "Calculating probabilities", "Tree diagrams", cls = "M")
    app.link_sub_topics_consecutively("Calculating probabilities", "Venn diagrams",
                                      "Mutually exclusive and independent events", cls = "M")


def create_statistical_distributions_maths():
    app.create_topic("Statistical Distributions/A_level")
    app.link_sub_topics_consecutively("Statistical Distributions/A_level", "Probability distributions/A_level",
                                      "Binomial distribution", "Cumulative probabilities", cls = "M")
    app.link_sub_topics_to_one("Probability distributions/A_level", "Sample space", "Probability mass function/A_level",
                               cls = "M")


def create_conditional_probability_maths():
    app.create_topic("Conditional probability/A_level")
    app.link_sub_topics_to_one("Conditional probability/A_level", "Set notation", "Conditional probability (sub_topic)",
                               cls = "M")
    app.link_sub_topics_to_one("Conditional probability (sub_topic)", "Venn diagrams with conditional probability",
                               "Probability formulae", cls = "M")
    app.create_relationships_consecutively("Conditional probability/A_level", "Tree diagrams")


def create_normal_distribution_a_lvl():
    app.create_topic("Normal distribution/A_level")
    app.link_sub_topics_to_one("Normal distribution/A_level", "The normal distribution",
                               "The inverse normal distribution function",
                               "The standard normal distribution", cls = "M")
    app.link_sub_topics_to_one("The normal distribution", "Finding probabilities for normal distributions",
                               "Finding μ and σ", "Approximating a binomial distribution",
                               "Hypothesis testing with the normal distribution", cls = "M")


def create_discrete_random_variables_fs1():
    app.create_topic("Discrete random variables/A_level")
    app.link_sub_topics_to_one("Discrete random variables/A_level", "Expected value of a discrete random variable",
                               "Variance of a discrete random variable", cls = "FS1")
    app.link_sub_topics_consecutively("Variance of a discrete random variable",
                                      "Expected value and variance of a function of X", cls = "FS1")
    app.create_relationships_consecutively("Expected value of a discrete random variable",
                                           "Expected value and variance of a function of X")


def create_more_distributions_fs1():
    app.create_topic("Poisson distributions")
    app.create_topic("Geometric and negative binomial distributions")
    app.link_sub_topics_to_one("Poisson distributions", "The Poisson distribution", cls = "FS1")
    app.link_sub_topics_to_one("Geometric and negative binomial distributions", "The geometric distribution",
                               "The negative binomial distribution", cls = "FS1")
    app.link_sub_topics_to_one("The Poisson distribution", "Mean and variance", "Adding Poisson distributions",
                               cls = "FS1")


def create_proof_maths():
    app.create_topic("Proof/A_level")
    app.link_sub_topics_to_one("Proof/A_level", "Proof by exhaustion", "Proof by contradiction/A_level",
                               "Proof by deduction", "Proof by counterexample", cls = "M")
    app.link_sub_topics_consecutively("Proof by contradiction/A_level", "Negation/A_level", cls = "M")


def create_proof_by_induction_cp():
    app.create_topic("Proof by induction")
    app.link_sub_topics_to_one("Proof by induction", "Proof by mathematical induction", "Proving divisibility results",
                               "Proving statements involving matrices", cls = "CP")


def create_proof_uni():
    app.create_topic("Proof/Cambridge_compsci")
    app.link_sub_topics_to_one("Proof/Cambridge_compsci", "Mathematical statements", "Divisibility and congruences",
                               "Fermat's Little Theorem", "Proof by contradiction",
                               "Proofs in practice and mathematical jargon", "Logical deduction", cls = "Uni")
    app.link_sub_topics_consecutively("Logical deduction", "Proof strategies and patterns", "Scratch work",
                                      "Logical equivalences", cls = "Uni")
    app.link_sub_topics_consecutively("Mathematical statements", "Implication", "Bi-implication",
                                      "Universal quantification", "Conjunction", "Existential quantification",
                                      "Disjunction", "Negation", cls = "Uni")


def create_number_theory_uni():
    app.create_topic("Number theory/Cambridge_compsci")
    app.link_sub_topics_to_one("Number theory/Cambridge_compsci", "Number systems",
                               "The division theorem and algorithm",
                               "Modular arithmetic", "Sets", "The greatest common divisor",
                               "The Diffie-Hellman cryptographic method", "Mathematical induction", cls = "Uni")
    app.link_sub_topics_consecutively("Number systems", "Natural numbers", "Integers", "Rationals", "Modular integers",
                                      cls = "Uni")
    app.link_sub_topics_consecutively("Sets", "Membership and comprehension", cls = "Uni")
    app.link_sub_topics_consecutively("The greatest common divisor", "Euclid's Algorithm and Theorem",
                                      "Extended Euclid's Algorithm", "Multiplicative inverses in modular arithmetic",
                                      cls = "Uni")
    app.link_sub_topics_consecutively("Mathematical induction", "Binomial Theorem", "Pascal's Triangle",
                                      "Fundamental Theorem of Arithmetic", "Euclid's infinity primes", cls = "Uni")


def create_number_theory_fp2():
    app.create_topic("Number theory/A_level")
    app.link_sub_topics_to_one("Number theory/A_level", "The division algorithm", "The Euclidean algorithm",
                               "Divisibility tests", "Modular arithmetic/A_level", "Fermat's Little Theorem/A_level",
                               "Combinatorics", cls = "FP2")
    app.link_sub_topics_consecutively("Divisibility tests", "Solving congruence equations", cls = "FP2")
    app.link_sub_topics_to_one("Combinatorics", "Subsets", "The empty set/A_level", cls = "FP2")


def create_continuous_distributions_fs2():
    app.create_topic("Continuous distributions/A_level")
    app.link_sub_topics_to_one("Continuous distributions/A_level", "Continuous random variables",
                               "The cumulative distribution function", cls = "FS2")


def create_algorithms_uni():
    app.create_topic("Algorithms")
    app.link_sub_topics_to_one("Algorithms", "Sorting", "Strategies for algorithm design", "Data structures",
                               "Graph algorithms", "Advanced data structures", "Geometric algorithms", cls = "Uni")

    app.link_sub_topics_to_one("Sorting", "Complexity and O-notation", "Merge sort", "Quick sort", "Heapsort",
                               "Stability", "Other sorting methods", "Median and order statistics", cls = "Uni")
    app.link_sub_topics_consecutively("Complexity and O-notation", "Sorting algorithms of quadratic complexity",
                                      cls = "Uni")
    app.link_sub_topics_consecutively("Quick sort", "Memory behaviour on statically allocated arrays", cls = "Uni")

    app.link_sub_topics_to_one("Strategies for algorithm design", "Dynamic programming", "Divide and conquer",
                               "Greedy algorithms", "Other paradigms", cls = "Uni")

    app.link_sub_topics_to_one("Graph algorithms", "Graph representations", "Breadth-first search",
                               "Depth-first search",
                               "Topological sort", "Minimum spanning tree", "Kruskal and Prim algorithms",
                               "Single-source shortest paths", "All-pairs shortest paths", "Maximum flow",
                               "Matchings in bipartite graphs", cls = "Uni")
    app.link_sub_topics_consecutively("Single-source shortest paths", "Bellman-Ford and Dijkstra algorithms",
                                      cls = "Uni")
    app.link_sub_topics_consecutively("All-pairs shortest paths", "Matrix multiplication", "Johnson's algorithm",
                                      cls = "Uni")
    app.link_sub_topics_to_one("Maximum flow", "Ford-Fulkerson method", "Max-Flow Min-Cut Theorem", cls = "Uni")


def create_advanced_algorithms_uni():
    app.create_topic("Advanced algorithms")
    app.link_sub_topics_to_one("Advanced algorithms", "Linear programming", "Approximation algorithms", cls = "Uni")

    app.link_sub_topics_to_one("Linear programming", "Definitions and applications", "Formulating linear programs",
                               "The simplex algorithm", "Finding initial solutions", cls = "Uni")
    app.create_relationships_consecutively("The simplex algorithm", "Finding initial solutions")

    app.link_sub_topics_to_one("Approximation algorithms", "Polynomial-time approximation schemes", "Design techniques",
                               "Applications", cls = "Uni")
    app.link_sub_topics_consecutively("Applications", "Vertex cover", "Subset-sum", "Parallel machine scheduling",
                                      "Travelling salesman problem", "Solving TSP with linear programming",
                                      "Hardness of approximation", cls = "Uni")


def create_business_studies():
    app.create_topic("Business studies")
    app.link_sub_topics_to_one("Business studies", "Project planning and management", cls = "Uni")
    app.link_sub_topics_consecutively("Project planning and management", "Role of a manager", "PERT and GANTT charts",
                                      "Critical path analysis", "Estimation techniques", "Monitoring", cls = "Uni")


def create_game_theory_and_game_playing():
    app.create_topic("Game theory")
    app.link_sub_topics_to_one("Game theory", "Choice between cooperation and conflict", "Prisoners' Dilemma",
                               cls = "Uni")
    app.link_sub_topics_consecutively("Prisoners' Dilemma", "Nash equilibrium", "Hawk-dove", "Iterated games",
                                      "Evolution of strategies", "Application to biology and computer science",
                                      cls = "Uni")

    app.create_topic("Game-playing")
    app.link_sub_topics_consecutively("Game-playing", "Search in an adversarial environment",
                                      "The minimax algorithm and its shortcomings",
                                      "Improving minimax using alpha-beta pruning", cls = "Uni")


def create_decision_maths_1():
    app.create_topic("Algorithms/A_level")
    app.link_sub_topics_to_one("Algorithms/A_level", "Using and understanding algorithms", "Bubble sort",
                               "Quick sort/A_level",
                               "Bin-packing algorithms", "Order of an algorithm", cls = "D1")

    app.create_topic("Graphs and networks")
    app.link_sub_topics_to_one("Graphs and networks", "Modelling with graphs", "Graph theory",
                               "The planarity algorithm",
                               cls = "D1")
    app.link_sub_topics_to_one("Graph theory", "Special types of graph",
                               "Representing graphs and networks using matrices",
                               cls = "D1")
    app.create_relationships_consecutively("Modelling with graphs", "Graph theory")

    app.create_topic("Algorithms on graphs")
    app.link_sub_topics_to_one("Algorithms on graphs", "Kruskal's algorithm", "Prim's algorithm",
                               "Dijkstra's algorithm to find shortest path", "Floyd's algorithm", cls = "D1")
    app.link_sub_topics_consecutively("Prim's algorithm", "Applying Prim's algorithm to a distance matrix", cls = "D1")

    app.create_topic("The travelling salesman problem")
    app.link_sub_topics_to_one("The travelling salesman problem",
                               "Classical and practical travelling salesman problems",
                               cls = "D1")
    app.link_sub_topics_to_one("Classical and practical travelling salesman problems",
                               "Using minimum spanning tree method to find an upper bound",
                               "Using minimum spanning tree method to find a lower bound",
                               "Using nearest neighbour algorithm to find an upper bound", cls = "D1")

    app.create_topic("Linear programming/A_level")
    app.link_sub_topics_to_one("Linear programming/A_level", "Linear programming problems", cls = "D1")
    app.link_sub_topics_to_one("Linear programming problems", "Graphical methods", "Locating the optimal point",
                               "Solutions with integer values",
                               cls = "D1")

    app.create_topic("The simplex algorithm/A_level")
    app.link_sub_topics_to_one("The simplex algorithm/A_level", "Formulating linear programming problems",
                               "The simplex method",
                               "Problems requiring integer solutions", "The Big-M method", cls = "D1")
    app.link_sub_topics_consecutively("The simplex method", "Two-stage simplex method", cls = "D1")

    app.create_topic("Critical path analysis/A_level")
    app.link_sub_topics_to_one("Critical path analysis/A_level", "Modelling a project", "Dummy activities",
                               "Gantt charts",
                               "Resource histograms", "Scheduling diagrams", cls = "D1")
    app.link_sub_topics_to_one("Dummy activities", "Early and late event times", "Critical activities",
                               "The float of an activity", cls = "D1")


def create_decision_maths_2():
    app.create_topic("Transportation problems")
    app.link_sub_topics_to_one("Transportation problems", "The north-west corner method",
                               "Unbalanced problems and degenerate solutions",
                               "Linear programming with transportation problems", cls = "D2")
    app.link_sub_topics_consecutively("Unbalanced problems and degenerate solutions", "Finding an improved solution",
                                      "The stepping-stone method", cls = "D2")

    app.create_topic("Allocation problems")
    app.link_sub_topics_to_one("Allocation problems", "The Hungarian algorithm", "Using a dummy",
                               "Maximum profit allocation",
                               "Managing incomplete data", "Linear programming with allocation problems", cls = "D2")

    app.create_topic("Flows in networks")
    app.link_sub_topics_to_one("Flows in networks", "Flows in networks (sub topic)", "Cuts and their capacities",
                               "Finding an initial flow", cls = "D2")
    app.link_sub_topics_consecutively("Finding an initial flow", "Flow-augmenting routes",
                                      "Maximum flow - minimum cut theorem", cls = "D2")
    app.link_sub_topics_to_one("Cuts and their capacities", "Lower capacities", "Sources and sinks",
                               "Restricted capacity nodes", cls = "D2")

    app.create_topic("Dynamic programming/A_level")
    app.link_sub_topics_to_one("Dynamic programming/A_level", "Shortest and longest path problems",
                               "Dynamic programming problems in table form", cls = "D2")
    app.link_sub_topics_consecutively("Shortest and longest path problems", "Minimax and maximin problems", cls = "D2")
    app.link_sub_topics_to_one("Shortest and longest path problems", "Bellman's principle of optimality", cls = "D2")

    app.create_topic("Game theory/A_level")
    app.link_sub_topics_to_one("Game theory/A_level", "Play-safe strategies and stable solutions",
                               "Converting games to linear programming problems", cls = "D2")
    app.link_sub_topics_to_one("Play-safe strategies and stable solutions", "Reducing the pay-off matrix",
                               "Optimal strategies for games with no stable solution", cls = "D2")
    app.link_sub_topics_consecutively("Play-safe strategies and stable solutions", "Prisoners' Dilemma/A_level",
                                      cls = "D2")


def create_sets_uni():
    app.create_topic("Set theory")
    app.link_sub_topics_to_one("Set theory", "Extensionality axiom", "Separation principle", "Powerset axiom",
                               "Pairing axiom",
                               "Union axiom", "Relations", "Partial and (total) functions", "Bijections",
                               "Equivalence relations and set partitions",
                               "Finite cardinality and counting", "Infinity axiom", "Surjections",
                               "Enumerable and countable sets", "Axiom of choice", "Injections", "Images",
                               "Replacement axiom", "Set cardinality", "Foundation axiom", cls = "Uni")
    app.link_sub_topics_consecutively("Extensionality axiom", "Subsets and supersets", cls = "Uni")
    app.link_sub_topics_consecutively("Separation principle", "Russell's Paradox", "The empty set", cls = "Uni")
    app.link_sub_topics_consecutively("Powerset axiom", "Powerset Boolean algebra", "Venn and Hasse diagrams",
                                      cls = "Uni")
    app.link_sub_topics_consecutively("Pairing axiom", "Singletons", "Ordered pairs", "Products", cls = "Uni")
    app.link_sub_topics_consecutively("Union axiom", "Big unions", "Big interjections", "Disjoint unions", cls = "Uni")
    app.link_sub_topics_consecutively("Relations", "Composition", "Matrices", "Directed graphs",
                                      "Preorders and partial orders", cls = "Uni")
    app.link_sub_topics_to_one("Bijections", "Sections and retractions", "Calculus of bijections", cls = "Uni")
    app.link_sub_topics_consecutively("Calculus of bijections", "Characteristic (or indicator) functions", cls = "Uni")
    app.link_sub_topics_consecutively("Images", "Direct and inverse images", cls = "Uni")
    app.link_sub_topics_consecutively("Replacement axiom", "Set-indexed constructions", cls = "Uni")
    app.link_sub_topics_consecutively("Set cardinality", "Cantor-Schoeder-Bernstein Theorem",
                                      "Unbounded cardinality", "Diagonalisation", "Fixed points", cls = "Uni")


def create_flow_control_uni():
    app.create_topic("Flow control and resource optimisation")
    app.link_sub_topics_to_one("Flow control and resource optimisation", "Control theory", "Stemming the flood",
                               "Optimisation as a model of network and user")


def create_matrix_algebra_fp2():
    app.create_topic("Matrix algebra")
    app.link_sub_topics_to_one("Matrix algebra", "Eigenvalues and eigenvectors", "Reducing matrices to diagonal form",
                               "The Cayley-Hamilton theorem", cls = "FP2")


def create_matrices_cp():
    app.create_topic("Matrices/A_level")
    app.link_sub_topics_to_one("Matrices/A_level", "Introduction to matrices", "Matrix multiplication/A_level",
                               "Determinants", cls = "CP")
    app.link_sub_topics_to_one("Determinants", "Inverting a 2 x 2 matrix", "Inverting a 3 x 3 matrix", cls = "CP")
    app.link_sub_topics_consecutively("Inverting a 3 x 3 matrix", "Solving systems of equations using matrices",
                                      cls = "CP")


def create_the_binomial_expansion_maths():
    app.create_topic("The binomial expansion")
    app.link_sub_topics_to_one("The binomial expansion", "Pascal's triangle/A_level", "Factorial notation",
                               "Binomial estimation", cls = "M")
    app.link_sub_topics_consecutively("Pascal's triangle/A_level", "The binomial expansion (sub topic)", cls = "M")
    app.create_relationships_consecutively("Factorial notation", "The binomial expansion (sub topic)")


def link_all():
    # link compulsory maths
    app.create_relationships_consecutively("Proof by contradiction/A_level", "Proof by contradiction")
    app.create_relationships_consecutively("Negation/A_level", "Negation")
    app.create_relationships_consecutively("Conditional probability/A_level", "Conditional probability")
    app.create_relationships_consecutively("Mutually exclusive and independent events", "Independence")
    app.create_relationships_consecutively("Cumulative probabilities", "Cumulative distribution")
    app.create_relationships_consecutively("Binomial distribution", "Binomial")
    app.create_relationships_consecutively("Probability space", "Sample space")
    app.create_relationships_consecutively("Probability distributions/A_level", "Probability distributions")

    app.create_relationships_consecutively("Probability mass function/A_level", "Probability mass function")
    app.create_relationships_consecutively("Mean", "Sample mean")
    app.create_relationships_consecutively("Variance and standard deviation", "Sample variance")
    app.create_relationships_consecutively("Proof by deduction", "Logical deduction")
    app.create_relationships_to_one("Binomial Theorem", "The binomial expansion (sub topic)", "Binomial distribution")
    app.create_relationships_consecutively("Pascal's triangle/A_level", "Pascal's Triangle")
    app.create_relationships_consecutively("Venn diagrams", "Venn diagrams with conditional probability",
                                           "Venn and Hasse diagrams")

    # link compulsory further maths
    app.create_relationships_to_many("Matrices/A_level", "Matrices")
    app.create_relationships_consecutively("Matrix multiplication/A_level", "Matrix multiplication")
    app.create_relationships_consecutively("Proof by mathematical induction", "Mathematical induction")

    # link further pure 1
    app.create_relationships_consecutively("Reducing matrices to diagonal form", "Diagonalisation")

    # link further pure 2
    app.create_relationships_consecutively("The Euclidean algorithm", "Euclid's Algorithm and Theorem")
    app.create_relationships_consecutively("Modular arithmetic/A_level", "Modular arithmetic")
    app.create_relationships_to_many("Fermat's Little Theorem/A_level", "Fermat's Little Theorem", "Proof/A_level")
    app.create_relationships_to_many("Solving congruence equations", "Proof/A_level", "Divisibility and congruences")
    app.create_relationships_consecutively("Combinatorics", "Counting/Combinatorics")
    app.create_relationships_consecutively("The division algorithm", "The division theorem and algorithm")
    app.create_relationships_consecutively("Subsets", "Subsets and supersets")
    app.create_relationships_consecutively("The empty set/A_level", "The empty set")

    # link further stats 1
    app.create_relationships_consecutively("Discrete random variables/A_level", "Discrete random variables")
    app.create_relationships_consecutively("Expected value and variance of a function of X", "Variance")
    app.create_relationships_consecutively("Normal and exponential distributions", "The normal distribution")
    app.create_relationships_to_one("Expected value of a discrete random variable", "Expectation", "Random variables")
    app.create_relationships_to_one("Mean and variance", "Binomial distribution", "The geometric distribution",
                                    "The negative binomial distribution", "Variance", "Continuous distributions")
    app.create_relationships_consecutively("Binomial distribution", "The negative binomial distribution")
    app.create_relationships_to_many("Applying to other distributions", "The Poisson distribution",
                                     "The geometric distribution",
                                     "Binomial distribution", "The negative binomial distribution")
    app.create_relationships_consecutively("The Poisson distribution", "Poisson")
    app.create_relationships_consecutively("The geometric distribution", "Geometric")
    app.create_relationships_consecutively("The central limit theorem", "Central Limit Theorem")
    app.create_relationships_consecutively("Expected value and variance of a function of X",
                                           "Definition and properties of expectation")

    # link further stats 2
    app.create_relationships_consecutively("The cumulative distribution function", "Cumulative distribution")
    app.create_relationships_consecutively("Continuous random variables", "Continuous distributions")

    # decision maths 1 and 2
    app.create_relationships_consecutively("Linear programming/A_level", "Linear programming",
                                           "Solving TSP with linear programming")
    app.create_relationships_to_one("Definitions and applications", "Linear programming with transportation problems",
                                    "Linear programming with allocation problems",
                                    "Converting games to linear programming problems")
    app.create_relationships_consecutively("Solutions with integer values", "Problems requiring integer solutions",
                                           "Finding initial solutions")
    app.create_relationships_consecutively("Linear programming problems", "Formulating linear programming problems",
                                           "Formulating linear programs")
    app.create_relationships_consecutively("Bubble sort", "Sorting algorithms of quadratic complexity")
    app.create_relationships_consecutively("Quick sort/A_level", "Quick sort")
    app.create_relationships_consecutively("Using and understanding algorithms", "Algorithms")
    app.create_relationships_consecutively("Graph theory", "Graph representations")
    app.create_relationships_to_one("Kruskal and Prim algorithms", "Kruskal's algorithm", "Prim's algorithm")
    app.create_relationships_consecutively("Dijkstra's algorithm to find shortest path",
                                           "Bellman-Ford and Dijkstra algorithms")
    app.create_relationships_consecutively("Maximum flow - minimum cut theorem", "Max-Flow Min-Cut Theorem")
    app.create_relationships_consecutively("Classical and practical travelling salesman problems",
                                           "Travelling salesman problem")
    app.create_relationships_consecutively("The simplex method", "The simplex algorithm")
    app.create_relationships_consecutively("Gantt charts", "PERT and GANTT charts")
    app.create_relationships_consecutively("Modelling a project", "Project planning and management")
    app.create_relationships_consecutively("Dynamic programming/A_level", "Dynamic programming")
    app.create_relationships_consecutively("Bellman's principle of optimality", "Bellman-Ford and Dijkstra algorithms")
    app.create_relationships_consecutively("Minimax and maximin problems", "The minimax algorithm and its shortcomings")
    app.create_relationships_consecutively("Prisoners' Dilemma/A_level", "Prisoners' Dilemma")
    app.create_relationships_to_one("Evolution of strategies", "Play-safe strategies and stable solutions",
                                    "Optimal strategies for games with no stable solution")


def show_compulsory_maths():
    create_measures_of_location_and_spread_maths()
    create_statistical_distributions_maths()
    create_proof_maths()
    create_probability_maths()
    create_conditional_probability_maths()
    create_the_binomial_expansion_maths()
    create_normal_distribution_a_lvl()


def show_compulsory_further_maths():
    show_compulsory_maths()
    create_matrices_cp()
    create_proof_by_induction_cp()


def show_uni():
    create_proof_uni()
    create_business_studies()
    create_game_theory_and_game_playing()
    create_algorithms_uni()
    create_advanced_algorithms_uni()
    create_number_theory_uni()
    create_probability_uni()
    create_sets_uni()


def show_fp2():
    create_number_theory_fp2()
    create_matrix_algebra_fp2()


def show_fs1():
    create_more_distributions_fs1()
    create_central_limit_theorem_fs1()
    create_discrete_random_variables_fs1()


def show_fs2():
    create_continuous_distributions_fs2()


def show_d1():
    create_decision_maths_1()


def show_d2():
    create_decision_maths_2()


if __name__ == "__main__":
    bolt_url = "bolt://localhost:7687"
    user = "neo4j"
    password = "boi"
    app = App(bolt_url, user, password)
    app.delete_all()
    show_uni()
    show_compulsory_maths()
    link_all()
    app.close()
