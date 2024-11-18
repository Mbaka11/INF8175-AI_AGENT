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

#### Optimization

The concept is divised in two:

* Direct Potential Optimization
* Evolutive Potential Optimization

grasping a better understanding of optimizing an heuristic, better evaluate each states to get a better variance between neighbors of a certain states, which will decrease the search time since less nodes are expanded when using a minimax, less equality,

Better tuning of the Piece Variance Heursitic, by make the city at the same level as the ressource  only when theres less city than ressource which gives a better variance compute, the goal is two have the most color possibilites to create or block divercity

![1731898067298](image/README/1731898067298.png)
