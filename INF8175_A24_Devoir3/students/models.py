import nn
from backend import PerceptronDataset, RegressionDataset, DigitClassificationDataset


class PerceptronModel(object):
    def __init__(self, dimensions: int) -> None:
        """
        Initialize a new Perceptron instance.

        A perceptron classifies data points as either belonging to a particular
        class (+1) or not (-1). `dimensions` is the dimensionality of the data.
        For example, dimensions=2 would mean that the perceptron must classify
        2D points.
        """
        self.w = nn.Parameter(1, dimensions)

    def get_weights(self) -> nn.Parameter:
        """
        Return a Parameter instance with the current weights of the perceptron.
        """
        return self.w

    def run(self, x: nn.Constant) -> nn.Node:
        """
        Calculates the score assigned by the perceptron to a data point x.

        Inputs:
            x: a node with shape (1 x dimensions)
        Returns: a node containing a single number (the score)
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 1 ***"
        return nn.DotProduct(self.w, x)

    def get_prediction(self, x: nn.Constant) -> int:
        """
        Calculates the predicted class for a single data point `x`.

        Returns: 1 or -1
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 1 ***"
        return 1 if nn.as_scalar(self.run(x)) >= 0 else -1

    def train(self, dataset: PerceptronDataset) -> None:
        """
        Train the perceptron until convergence.
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 1 ***"
        all_matching = False
        
        while not all_matching:
            all_matching = True
            for x, y in dataset.iterate_once(1):
                if self.get_prediction(x) != nn.as_scalar(y):           # En d'autres termes, avec les notions du cours: if y_real != y_pred (y_hat)
                    all_matching = False                                # On continue la boucle, car on a trouvé une erreur
                    self.w.update(x, nn.as_scalar(y))                   # On met à jour les poids du perceptron


class RegressionModel(object):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """

    def __init__(self) -> None:
        # Initialize your model parameters here
        "*** TODO: COMPLETE HERE FOR QUESTION 2 ***"
        #nombre de neurones dans la couche cachée
        self.hidden_layer_size = 100
        
        #poids de la couche cachée
        self.w1 = nn.Parameter(1, self.hidden_layer_size)
        #biais de la couche cachée
        self.b1 = nn.Parameter(1, self.hidden_layer_size)
        
        #poids de la couche de sortie
        self.w2 = nn.Parameter(self.hidden_layer_size, 1)
        #biais de la couche de sortie
        self.b2 = nn.Parameter(1, 1)

    def run(self, x: nn.Constant) -> nn.Node:
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
        Returns:
            A node with shape (batch_size x 1) containing predicted y-values
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 2 ***"
        y_pred1 = nn.AddBias(nn.Linear(x, self.w1), self.b1)
        activation = nn.ReLU(y_pred1)
        y_pred2 = nn.AddBias(nn.Linear(activation, self.w2), self.b2)
        return y_pred2
        

    def get_loss(self, x: nn.Constant, y: nn.Constant) -> nn.Node:
        """
        Computes the loss for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
            y: a node with shape (batch_size x 1), containing the true y-values
                to be used for training
        Returns: a loss node
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 2 ***"
        return nn.SquareLoss(self.run(x), y)

    def train(self, dataset: RegressionDataset) -> None:
        """
        Trains the model.
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 2 ***"
        learning_rate = 0.01
        max_loss = 0.02
        batch_size = 10
        
        while True:
            loss = 0
            for x, y in dataset.iterate_once(batch_size):
                loss += nn.as_scalar(self.get_loss(x, y))
                grad_w1, grad_b1, grad_w2, grad_b2 = nn.gradients(self.get_loss(x, y), [self.w1, self.b1, self.w2, self.b2])
                self.w1.update(grad_w1, -learning_rate)
                self.b1.update(grad_b1, -learning_rate)
                self.w2.update(grad_w2, -learning_rate)
                self.b2.update(grad_b2, -learning_rate)
                
            if loss < max_loss:
                break

class DigitClassificationModel(object):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """

    def __init__(self) -> None:
        # Initialize your model parameters here
        "*** TODO: COMPLETE HERE FOR QUESTION 3 ***"
        self.input_size = 784
        # nombre de neurones dans la couche cachée et nombre de pixels dans l'image
        self.hidden_layer_size = 256
        # nombre de classes possibles
        self.output_size = 10
        
        # poids de la couche cachée
        self.w1 = nn.Parameter(self.input_size, self.hidden_layer_size)
        # biais de la couche cachée
        self.b1 = nn.Parameter(1, self.hidden_layer_size)
        
        # poids de la couche de sortie
        self.w2 = nn.Parameter(self.hidden_layer_size, self.output_size)
        # biais de la couche de sortie
        self.b2 = nn.Parameter(1, self.output_size)

    def run(self, x: nn.Constant) -> nn.Node:
        """
        Runs the model for a batch of examples.

        Your model should predict a node with shape (batch_size x 10),
        containing scores. Higher scores correspond to greater probability of
        the image belonging to a particular class.

        Inputs:
            x: a node with shape (batch_size x 784)
        Output:
            A node with shape (batch_size x 10) containing predicted scores
                (also called logits)
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 3 ***"
        y_pred1 = nn.AddBias(nn.Linear(x, self.w1), self.b1)
        activation = nn.ReLU(y_pred1)
        y_pred2 = nn.AddBias(nn.Linear(activation, self.w2), self.b2)
        return y_pred2

    def get_loss(self, x: nn.Constant, y: nn.Constant) -> nn.Node:
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 10). Each row is a one-hot vector encoding the correct
        digit class (0-9).

        Inputs:
            x: a node with shape (batch_size x 784)
            y: a node with shape (batch_size x 10)
        Returns: a loss node
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 3 ***"
        return nn.SoftmaxLoss(self.run(x), y)

    def train(self, dataset: DigitClassificationDataset) -> None:
        """
        Trains the model.
        """
        "*** TODO: COMPLETE HERE FOR QUESTION 3 ***"
        learning_rate = 0.01
        validation_precision = 0.97
        
        while True:
            for x, y in dataset.iterate_once(4):
                grad_w1, grad_b1, grad_w2, grad_b2 = nn.gradients(self.get_loss(x, y), [self.w1, self.b1, self.w2, self.b2])
                self.w1.update(grad_w1, -learning_rate)
                self.b1.update(grad_b1, -learning_rate)
                self.w2.update(grad_w2, -learning_rate)
                self.b2.update(grad_b2, -learning_rate)
                
            if dataset.get_validation_accuracy() > validation_precision:
                break
