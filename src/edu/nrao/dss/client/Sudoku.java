package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

class Sudoku {
    /** Return a list of those sessions the user needs to be most concerned about. */
    public List<Window> findProblem(List<Window> windows) {
        // Convert in...
        ArrayList<WindowProxy> proxies = new ArrayList<WindowProxy>();
        for (Window window : windows) {
            proxies.add(new WindowProxy(window));
        }

        // Process...
        List<WindowProxy> problem = findProblem1(proxies);
        if (problem == null) {
            return null;
        }

        // Convert out...
        ArrayList<Window> result = new ArrayList<Window>();
        for (WindowProxy window : problem) {
            result.add(window.getWindow());
        }

        return result;
    }

    /** Return a list of those sessions the user needs to be most concerned about. */
    private List<WindowProxy> findProblem1(List<WindowProxy> sessions) {
        // Find the distinct subsets of the input.
        List<List<WindowProxy>> partitions = partition(sessions);

        // We'll deal with the smallest partitions first, in the name of expediency.
        Collections.sort(partitions, new Comparator<List<WindowProxy>>() {
            public int compare(List<WindowProxy> lhs, List<WindowProxy> rhs) {
                if (lhs.size() < rhs.size()) { return -1; }
                if (rhs.size() < lhs.size()) { return +1; }
                return 0;
            }
        });

        // Return the first problem identified, if any.
        for (List<WindowProxy> partition : partitions) {
            if (isProblem(partition)) {
                return partition;
            }
        }

        // No problems found.
        return null;
    }

    /** Decide if a specific group of sessions is a problem. */
    private boolean isProblem(List<WindowProxy> sessions) {
        if (! trivialElimination(sessions)) {
            return true;
        }

        if (! computationallyFeasible(sessions)) {
            return true;
        }

        if (! sudokuElimination(sessions)) {
            return true;
        }

        return false;
    }

    private boolean trivialElimination(List<WindowProxy> sessions) {
        while (sessions.size() > 0) {
            Collections.sort(sessions, new Comparator<WindowProxy>() {
                public int compare(WindowProxy lhs, WindowProxy rhs) {
                    if (lhs.getNumIntervals() < rhs.getNumIntervals()) { return -1; }
                    if (rhs.getNumIntervals() < lhs.getNumIntervals()) { return +1; }
                    return 0;
                }
            });

            if (sessions.get(0).getNumIntervals() == 0) {
                return false;
            }
            if (sessions.get(0).getNumIntervals()  > 1) {
                return true;
            }
            if (sessions.get(0).getNumIntervals() == 1) {
                Interval interval = sessions.get(0).getInterval(0);
                for (WindowProxy session : sessions) {
                    session.nukeInterval(interval);
                }
                sessions.remove(sessions.get(0));
            }
        }

        return true;
    }

    private boolean computationallyFeasible(List<WindowProxy> sessions) {
        int size = 1;
        for (WindowProxy session : sessions) {
            size *= session.getNumIntervals();
            if (size > THRESHOLD) {
                return false;
            }
        }

        return true;
    }

    private boolean sudokuElimination(List<WindowProxy> sessions) {
        // Succeed.
        if (sessions.size() == 0) {
            return true;
        }

        Collections.sort(sessions, new Comparator<WindowProxy>() {
            public int compare(WindowProxy lhs, WindowProxy rhs) {
                if (lhs.getNumIntervals() < rhs.getNumIntervals()) { return -1; }
                if (rhs.getNumIntervals() < lhs.getNumIntervals()) { return +1; }
                return 0;
            }
        });

        // Fail.
        if (sessions.get(0).getNumIntervals() == 0) {
            return false;
        }

        // Only one option, recur.
        if (sessions.get(0).getNumIntervals() == 1) {
            Interval interval = sessions.get(0).getInterval(0);
            for (WindowProxy session : sessions) {
                session.nukeInterval(interval);
            }
            sessions.remove(sessions.get(0));
            return sudokuElimination(sessions);
        }

        // Multiple options, try them each.
        for (Interval interval : sessions.get(0).getIntervals()) {
            ArrayList<WindowProxy> proxies = new ArrayList<WindowProxy>();
            for (int i = 1; i < sessions.size(); ++i) {
                WindowProxy proxy = new WindowProxy(sessions.get(i));
                proxy.nukeInterval(interval);
            }

            // Succeed.
            if (sudokuElimination(proxies)) {
                return true;
            }
        }

        // Fail.
        return false;
    }

    /** Organize a list of sessions into mutually-exclusive subsets. */
    private List<List<WindowProxy>> partition(List<WindowProxy> sessions) {
        int         n         = sessions.size();
        boolean[][] conflicts = new boolean[n][n];

        // Initialize with direct conflicts.
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (sessions.get(i).conflicts(sessions.get(j))) { conflicts[i][j] = true; }
            }
        }

        // Floyd-Warshall algorithm for transitive closure.
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                for (int k = 0; k < n; ++k) {
                    conflicts[i][j] |= conflicts[i][k] && conflicts[k][j];
                }
            }
        }

        // Traverse the resulting graph.
        List<List<WindowProxy>> result  = new ArrayList<List<WindowProxy>>();
        boolean[]                visited = new boolean[n];
        for (int i = 0; i < n; ++i) {
            if (visited[i]) { continue; }

            ArrayList<WindowProxy> group = new ArrayList<WindowProxy>();
            for (int j = 0; j < n; ++j) {
                if (conflicts[i][j]) {
                    group.add(sessions.get(j));
                    visited[j] = true;
                }
            }

            result.add(group);
        }

        return result;
    }

    private static final int THRESHOLD = 1000000;
}
