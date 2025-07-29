| **Distance / Similarity Type** | **Best Use Cases**                                                                             | **Examples**                                              |
| ------------------------------ | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **L1 (Manhattan Distance)**    | - High-dimensional numeric data<br>- Robust to outliers<br>- Clustering with additive features | Comparing pixel intensities, tabular ML features          |
| **L2 (Euclidean Distance)**    | - Low-dimensional real-world measurements<br>- Geometric distance<br>- K-NN, K-Means           | GPS coordinates, image feature vectors                    |
| **Negative Inner Product**     | - Model-generated embeddings<br>- Neural search<br>- Dot product based models                  | Sentence transformers, collaborative filtering embeddings |
| **Cosine Similarity**          | - Semantic similarity<br>- Normalized high-dimensional vectors<br>- Text/document embeddings   | BERT embeddings, TF-IDF vectors, user/item profiles       |
| **Cosine Distance (1 - sim)**  | - Clustering/search where length doesn’t matter<br>- Embedding similarity ranking              | Semantic search, document clustering                      |
| **Hamming Distance**           | - Binary feature comparison<br>- Symbol sequence mismatch<br>- Error checking                  | DNA strings, binary hash keys, one-hot encoded vectors    |
| **Jaccard Similarity**         | - Set overlap comparison<br>- Sparse binary vectors<br>- Unique keyword/tag overlap            | Plagiarism detection (n-grams), user-liked item sets      |
| **Jaccard Distance (1 - sim)** | - Binary/set dissimilarity<br>- Set-based clustering<br>- Sparse feature deduplication         | Tag-based product clustering, document deduplication      |
