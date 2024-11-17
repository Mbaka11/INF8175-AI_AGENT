# La Cité De Dieux

## Whats left

* Meilleurs opening moves
* isQuiescent
* MCTS + Minimax
* Tuning Variance Heuristique

## Ameliration

#### Cache

LFU Cache -> LRU  Cache + Managing symmetric moves

#### PointDifference Heuristic

added decision based solely on maximzing the difference of points

#### Better utility function

instead of returning the 1 when winning and -1 when losiing returning the difference of poiints at the end of the game help the agent maximizing our point point difference and choose the best out come scneario

#### Better PointDifference Heuristic

Explication added in notes

#### Variance heuristic

Make decision with the variance which increase our chance of creating divercity , block and get points

![1731819299567](image/README/1731819299567.png)

#### Normalization

added a better version of normalize, instead of sigmoid it is now a min max scaling

give us way better play and can better differenciate and quantify a certain state since the change in value was too great with sigmoid

![1731786625299](image/README/1731786625299.png)
