
| ==Special Ops== | ==Extension== |
| --------------- | ------------- |
| pgvector        |               |

# DDL

| ==DB/FEATURE== | ==Create <br>Collection== | ==Alter <br>Collection== | ==Drop<br>Collection== |
| -------------- | ------------------------- | ------------------------ | ---------------------- |
| **pgvector**   |                           |                          |                        |
|                |                           |                          |                        |
|                |                           |                          |                        |

---
# DML

| ==DB/FEATURE== | ==Insert <br>Into<br>Collection== | ==Upsert <br>Into<br>Collection== | ==Delete<br>From<br>Collection== |
| -------------- | --------------------------------- | --------------------------------- | -------------------------------- |
| **pgvector**   |                                   |                                   |                                  |

---
# DQL
| ==DB/FEATURE== | ==L1 or<br>Manhattan<br>Distance== | ==L2 or<br>Euclidian<br>Distance== | ==Negative<br>Inner<br>Product== | ==Cosine<br>Distance== | ==Cosine<br>Similarity== | ==Hamming<br>Distance== | ==Jaccard<br>Distance== | ==Jaccard<br>Similarity== |
| -------------- | ---------------------------------- | ---------------------------------- | -------------------------------- | ---------------------- | ------------------------ | ----------------------- | ----------------------- | ------------------------- |
| **pgvector**   | <+>                                | <->                                | <#>                              | <=>                    | 1-<=>                    | <~>                     | 1-<%>                   |                           |
|                |                                    |                                    |                                  |                        |                          |                         |                         |                           |

---
