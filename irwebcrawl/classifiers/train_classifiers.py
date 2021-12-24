import os

import graphviz
import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree._tree import TREE_LEAF
import joblib

from irwebcrawl.features.feature_extraction import Extractor


def is_leaf(inner_tree, index):
    # Check whether node is leaf node
    return (inner_tree.children_left[index] == TREE_LEAF and
            inner_tree.children_right[index] == TREE_LEAF)


def prune_index(inner_tree, decisions, index=0):
    # Start pruning from the bottom - if we start from the top, we might miss
    # nodes that become leaves during pruning.
    # Do not use this directly - use prune_duplicate_leaves instead.
    if not is_leaf(inner_tree, inner_tree.children_left[index]):
        prune_index(inner_tree, decisions, inner_tree.children_left[index])
    if not is_leaf(inner_tree, inner_tree.children_right[index]):
        prune_index(inner_tree, decisions, inner_tree.children_right[index])

    # Prune children if both children are leaves now and make the same decision:
    if (is_leaf(inner_tree, inner_tree.children_left[index]) and
        is_leaf(inner_tree, inner_tree.children_right[index]) and
        (decisions[index] == decisions[inner_tree.children_left[index]]) and
        (decisions[index] == decisions[inner_tree.children_right[index]])):
        # turn node into a leaf by "unlinking" its children
        inner_tree.children_left[index] = TREE_LEAF
        inner_tree.children_right[index] = TREE_LEAF
        ##print("Pruned {}".format(index))


def prune_duplicate_leaves(mdl):
    # Remove leaves if both
    decisions = mdl.tree_.value.argmax(axis=2).flatten().tolist() # Decision for each node
    prune_index(mdl.tree_, decisions)


def main():
    decision_tree_ngram = tree.DecisionTreeClassifier()
    decision_tree_ngram_metrics = pipeline('../datasets/ngram_features.csv', decision_tree_ngram)
    print('Decision tree with ngrams')
    print(decision_tree_ngram_metrics)
    decision_tree_tokens = tree.DecisionTreeClassifier()
    decision_tree_tokens_metrics = pipeline('../datasets/token_features.csv', decision_tree_tokens)
    print('Decision tree with tokens')
    print(decision_tree_tokens_metrics)
    decision_tree_ngram_4 = tree.DecisionTreeClassifier(max_depth=4)
    decision_tree_ngram_4_metrics = pipeline('../datasets/ngram_features.csv', decision_tree_ngram_4)
    print('Decision tree with ngrams max depth 4')
    print(decision_tree_ngram_4_metrics)
    decision_tree_tokens_4 = tree.DecisionTreeClassifier(max_depth=4)
    decision_tree_tokens_4_metrics = pipeline('../datasets/token_features.csv', decision_tree_tokens_4)
    print('Decision tree with tokens max depth 4')
    print(decision_tree_tokens_4_metrics)
    decision_tree_token_ccp_0001 = tree.DecisionTreeClassifier(ccp_alpha=0.0001)
    decision_tree_token_ccp_0001_metrics = pipeline('../datasets/token_features.csv', decision_tree_token_ccp_0001)
    print('Decision tree with tokens pruned ccp alpha = 0.0001')
    print(decision_tree_token_ccp_0001_metrics)
    decision_tree_token_ccp_00001 = tree.DecisionTreeClassifier(ccp_alpha=0.00001)
    decision_tree_token_ccp_00001_metrics = pipeline('../datasets/token_features.csv', decision_tree_token_ccp_00001)
    print('Decision tree with tokens pruned ccp alpha = 0.00001')
    print(decision_tree_token_ccp_00001_metrics)
    decision_tree_ngram_ccp_00001 = tree.DecisionTreeClassifier(ccp_alpha=0.00001)
    decision_tree_ngram_ccp_00001_metrics = pipeline('../datasets/ngram_features.csv', decision_tree_ngram_ccp_00001)
    print('Decision tree with ngrams pruned ccp alpha = 0.00001')
    print(decision_tree_ngram_ccp_00001_metrics)
    decision_tree_ngram_ccp_0001 = tree.DecisionTreeClassifier(ccp_alpha=0.0001)
    decision_tree_ngram_ccp_0001_metrics = pipeline('../datasets/ngram_features.csv', decision_tree_ngram_ccp_0001)
    print('Decision tree with ngrams pruned ccp alpha = 0.0001')
    print(decision_tree_ngram_ccp_0001_metrics)

    best_tree = tree.DecisionTreeClassifier(ccp_alpha=0.00001, min_samples_leaf=50)
    best_tree_metrics = pipeline('../datasets/ngram_features.csv', best_tree)
    print('Decision tree with ngrams pruned ccp alpha = 0.00001, min samples in leaf = 50')
    print(best_tree_metrics)
    prune_duplicate_leaves(best_tree)
    joblib.dump(best_tree, 'decision_tree.joblib')

    names = ['dutch_domain', 'other_domain', 'dict_count', 'city_count', 'trained_dict_count', 'hyphen_count']

    random_forest = RandomForestClassifier(ccp_alpha=0.00001)
    random_forest_metrics = pipeline('../datasets/ngram_features.csv', random_forest)
    print('Random forest based on ngrams, alpha 0.00001')
    print(random_forest_metrics)

    importances = random_forest.feature_importances_
    std = np.std([tree_.feature_importances_ for tree_ in random_forest.estimators_], axis=0)
    forest_importances = pd.Series(importances, index=names)

    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_title("Feature importances using MDI")
    ax.set_ylabel("Mean decrease in impurity")
    fig.tight_layout()
    plt.show()

    dot_data = tree.export_graphviz(decision_tree_ngram_ccp_0001, out_file=None, feature_names=names,
                                    class_names=['non-Dutch', 'Dutch'])
    graph = graphviz.Source(dot_data)
    graph.render('pruned_0001')

    '''
    dot_data = tree.export_graphviz(decision_tree_ngram_ccp_00001, out_file=None, feature_names=names,
                                    class_names=['non-Dutch', 'Dutch'])
    graph = graphviz.Source(dot_data)
    graph.render('pruned_00001')
    '''

    dot_data = tree.export_graphviz(best_tree, out_file=None, feature_names=names,
                                    class_names=['non-Dutch', 'Dutch'])
    graph = graphviz.Source(dot_data)
    graph.render('best')


def pipeline(data_path, classifier):
    x, y = prepare_data(data_path)
    metrics = cross_validate(classifier, x, y)

    return metrics


def prepare_data(data_path):
    df = pd.read_csv(data_path)
    y = df['y']
    x = df.drop('y', axis=1)

    return x, y


def cross_validate(classifier, x, y):
    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    total_metrics = {}

    for train_index, val_index in kf.split(x):
        x_train, x_validate = x.iloc[train_index], x.iloc[val_index]
        y_train, y_validate = y.iloc[train_index], y.iloc[val_index]

        classifier.fit(x_train, y_train)
        cur_metrics = compute_metrics(y_validate, classifier.predict(x_validate))

        for metric, value in cur_metrics.items():
            if metric in total_metrics:
                values = total_metrics[metric]
                values.append(value)
            else:
                total_metrics[metric] = [value]

    for metric, values in total_metrics.items():
        total_metrics[metric] = np.mean(values)

    return total_metrics


def compute_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)

    return {'accuracy': accuracy, 'f-measure': f1, 'precision': precision, 'recall': recall}


def test_prediction():
    root_dir = os.path.abspath(os.path.dirname(__file__))
    classifier_path = os.path.join(root_dir, '../classifiers/decision_tree.joblib')
    url_classifier = joblib.load(classifier_path)
    extractor = Extractor()
    url = 'https://nos.nl/liveblog/2407093-reizigers-uit-zuid-afrika-vast-op-schiphol-nijmegen-verbiedt-demonstratie'
    features = np.array(extractor.extract_features(url)).reshape(1, -1)
    result = url_classifier.predict(features)
    success = result[0] == 1

    return success


if __name__ == '__main__':
    main
