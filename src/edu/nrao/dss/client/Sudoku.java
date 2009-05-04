package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

class Sudoku {
    /** Return a list of those sessions the user needs to be most concerned about. */
    public List<Session> findProblem(List<Session> sessions) {
        // Convert in...
        ArrayList<SessionProxy> proxies = new ArrayList<SessionProxy>();
        for (Session session : sessions) {
            proxies.add(new SessionProxy(session));
        }

        // Process...
        List<SessionProxy> problem = findProblem1(proxies);
        if (problem == null) {
            return null;
        }

        // Convert out...
        ArrayList<Session> result = new ArrayList<Session>();
        for (SessionProxy session : problem) {
            result.add((Session) session.getSession());
        }

        return result;
    }

    /** Return a list of those sessions the user needs to be most concerned about. */
    private List<SessionProxy> findProblem1(List<SessionProxy> sessions) {
        // Find the distinct subsets of the input.
        List<List<SessionProxy>> partitions = partition(sessions);

        // We'll deal with the smallest partitions first, in the name of expediency.
        Collections.sort(partitions, new Comparator<List<SessionProxy>>() {
            public int compare(List<SessionProxy> lhs, List<SessionProxy> rhs) {
                if (lhs.size() < rhs.size()) { return -1; }
                if (rhs.size() < lhs.size()) { return +1; }
                return 0;
            }
        });

        // Return the first problem identified, if any.
        for (List<SessionProxy> partition : partitions) {
            if (isProblem(partition)) {
                return partition;
            }
        }

        // No problems found.
        return null;
    }

    /** Decide if a specific group of sessions is a problem. */
    private boolean isProblem(List<SessionProxy> sessions) {
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

    private boolean trivialElimination(List<SessionProxy> sessions) {
        while (sessions.size() > 0) {
            Collections.sort(sessions, new Comparator<SessionProxy>() {
                public int compare(SessionProxy lhs, SessionProxy rhs) {
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
                for (SessionProxy session : sessions) {
                    session.nukeInterval(interval);
                }
                sessions.remove(sessions.get(0));
            }
        }

        return true;
    }

    private boolean computationallyFeasible(List<SessionProxy> sessions) {
        int size = 1;
        for (SessionProxy session : sessions) {
            size *= session.getNumIntervals();
            if (size > THRESHOLD) {
                return false;
            }
        }

        return true;
    }

    private boolean sudokuElimination(List<SessionProxy> sessions) {
        // Succeed.
        if (sessions.size() == 0) {
            return true;
        }

        Collections.sort(sessions, new Comparator<SessionProxy>() {
            public int compare(SessionProxy lhs, SessionProxy rhs) {
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
            for (SessionProxy session : sessions) {
                session.nukeInterval(interval);
            }
            sessions.remove(sessions.get(0));
            return sudokuElimination(sessions);
        }

        // Multiple options, try them each.
        for (Interval interval : sessions.get(0).getIntervals()) {
            ArrayList<SessionProxy> proxies = new ArrayList<SessionProxy>();
            for (int i = 1; i < sessions.size(); ++i) {
                SessionProxy proxy = new SessionProxy(sessions.get(i));
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
    private List<List<SessionProxy>> partition(List<SessionProxy> sessions) {
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
        List<List<SessionProxy>> result  = new ArrayList<List<SessionProxy>>();
        boolean[]                visited = new boolean[n];
        for (int i = 0; i < n; ++i) {
            if (visited[i]) { continue; }

            ArrayList<SessionProxy> group = new ArrayList<SessionProxy>();
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
