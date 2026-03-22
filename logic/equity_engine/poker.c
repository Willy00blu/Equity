#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

// --- RNG ULTRA-VELOCE (XorShift128) ---
static uint32_t x = 123456789;
static uint32_t y = 362436069;
static uint32_t z = 521288629;
static uint32_t w = 88675123;

void seed_rng() {
    srand((unsigned int)time(NULL));
    x = rand(); y = rand(); z = rand(); w = rand();
}

uint32_t xorshift128(void) {
    uint32_t t = x ^ (x << 11);
    x = y; y = z; z = w;
    return w = w ^ (w >> 19) ^ t ^ (t >> 8);
}

// --- SHUFFLE ---
void shuffle_deck(int *deck, int size) {
    for (int i = size - 1; i > 0; i--) {
        int j = xorshift128() % (i + 1);
        int temp = deck[i];
        deck[i] = deck[j];
        deck[j] = temp;
    }
}

// --- HELPER SCALA ---
static int find_straight_high_from_mask(unsigned int mask) {
    if ((mask & (1 << 12)) && (mask & 1) && (mask & (1 << 1)) &&
        (mask & (1 << 2)) && (mask & (1 << 3))) {
        return 3; 
    }
    for (int r = 12; r >= 4; r--) {
        unsigned int needed = (1u << r) | (1u << (r - 1)) |
                              (1u << (r - 2)) | (1u << (r - 3)) |
                              (1u << (r - 4));
        if ((mask & needed) == needed) return r;
    }
    return -1;
}

// --- VALUTATORE ---
int evaluate_7_cards(int *cards) {
    int ranks[13];
    int suits[4];
    
    // Reset manuale (più sicuro in C puro se non si usa {0} ovunque)
    memset(ranks, 0, sizeof(ranks));
    memset(suits, 0, sizeof(suits));

    for (int i = 0; i < 7; i++) {
        int r = cards[i] % 13;
        int s = cards[i] / 13;
        ranks[r]++;
        suits[s]++;
    }

    unsigned int rank_mask = 0;
    for (int r = 0; r < 13; r++) if (ranks[r] > 0) rank_mask |= (1u << r);

    int flush_suit = -1;
    for (int s = 0; s < 4; s++) if (suits[s] >= 5) { flush_suit = s; break; }

    int four_rank = -1;
    int trips[2] = {-1, -1}; int trip_count = 0;
    int pairs[3] = {-1, -1, -1}; int pair_count = 0;

    for (int r = 12; r >= 0; r--) {
        if (ranks[r] == 4) four_rank = r;
        else if (ranks[r] == 3) { if (trip_count < 2) trips[trip_count++] = r; }
        else if (ranks[r] == 2) { if (pair_count < 3) pairs[pair_count++] = r; }
    }

    int straight_high = find_straight_high_from_mask(rank_mask);
    
    if (flush_suit != -1) {
        unsigned int flush_rank_mask = 0;
        for (int i = 0; i < 7; i++) {
            if ((cards[i] / 13) == flush_suit) flush_rank_mask |= (1u << (cards[i] % 13));
        }
        int sf_high = find_straight_high_from_mask(flush_rank_mask);
        if (sf_high != -1) return (8 << 24) | (sf_high << 20); 
    }

    if (four_rank != -1) {
        int kicker = -1;
        for (int r = 12; r >= 0; r--) if (r != four_rank && ranks[r] > 0) { kicker = r; break; }
        return (7 << 24) | (four_rank << 20) | (kicker << 16);
    }

    if (trip_count >= 2) return (6 << 24) | (trips[0] << 20) | (trips[1] << 16); 
    if (trip_count == 1 && pair_count >= 1) return (6 << 24) | (trips[0] << 20) | (pairs[0] << 16); 

    if (flush_suit != -1) {
        int flush_ranks[5] = {0}, idx=0;
        for (int r = 12; r >= 0 && idx < 5; r--) {
            int present=0;
            for(int i=0; i<7; i++) if(cards[i]/13 == flush_suit && cards[i]%13 == r) present=1;
            if(present) flush_ranks[idx++] = r;
        }
        return (5 << 24) | (flush_ranks[0] << 20) | (flush_ranks[1] << 16) | (flush_ranks[2] << 12);
    }

    if (straight_high != -1) return (4 << 24) | (straight_high << 20);

    if (trip_count == 1) {
        int kickers[2]={0}, idx=0;
        for(int r=12; r>=0 && idx<2; r--) if(r!=trips[0] && ranks[r]>0) kickers[idx++]=r;
        return (3 << 24) | (trips[0] << 20) | (kickers[0] << 16) | (kickers[1] << 12);
    }

    if (pair_count >= 2) {
        int kicker = -1;
        for(int r=12; r>=0; r--) if(r!=pairs[0] && r!=pairs[1] && ranks[r]>0) { kicker=r; break; }
        return (2 << 24) | (pairs[0] << 20) | (pairs[1] << 16) | (kicker << 12);
    }

    if (pair_count == 1) {
        int kickers[3]={0}, idx=0;
        for(int r=12; r>=0 && idx<3; r--) if(r!=pairs[0] && ranks[r]>0) kickers[idx++]=r;
        return (1 << 24) | (pairs[0] << 20) | (kickers[0] << 16) | (kickers[1] << 12) | (kickers[2] << 8);
    }

    int singles[5]={0}, idx=0;
    for(int r=12; r>=0 && idx<5; r--) if(ranks[r]>0) singles[idx++]=r;
    return (0 << 24) | (singles[0] << 20) | (singles[1] << 16);
}

// --- FUNZIONE PRINCIPALE EXPORTED ---
// Niente extern "C" perché siamo già in C
void run_montecarlo_sim(
    int *hero_cards, 
    int *villain_cards, 
    int *board_cards, 
    int board_count, 
    int sims,
    int *out_wins,      
    int *out_ties,      
    int *out_total,
    int *out_stats      
) {
    seed_rng();
    
    int wins = 0;
    int ties = 0;
    
    // Reset stats array
    for(int i=0; i<9; i++) out_stats[i] = 0;

    int known_mask[52] = {0};
    known_mask[hero_cards[0]] = 1; known_mask[hero_cards[1]] = 1;
    known_mask[villain_cards[0]] = 1; known_mask[villain_cards[1]] = 1;
    for(int i=0; i<board_count; i++) known_mask[board_cards[i]] = 1;

    int clean_deck[52]; 
    int clean_deck_size = 0;
    for(int i=0; i<52; i++) if(!known_mask[i]) clean_deck[clean_deck_size++] = i;

    int working_deck[52];
    int hero_full[7], villain_full[7];
    
    hero_full[0] = hero_cards[0]; hero_full[1] = hero_cards[1];
    villain_full[0] = villain_cards[0]; villain_full[1] = villain_cards[1];

    for(int s=0; s<sims; s++) {
        memcpy(working_deck, clean_deck, clean_deck_size * sizeof(int));
        shuffle_deck(working_deck, clean_deck_size);

        for(int k=0; k<board_count; k++) {
            hero_full[2+k] = board_cards[k];
            villain_full[2+k] = board_cards[k];
        }
        int cards_needed = 5 - board_count;
        for(int k=0; k<cards_needed; k++) {
            hero_full[2+board_count+k] = working_deck[k];
            villain_full[2+board_count+k] = working_deck[k];
        }

        int score_hero = evaluate_7_cards(hero_full);
        int score_villain = evaluate_7_cards(villain_full);

        // Estrazione statistiche (bitwise shift)
        int hero_cat = score_hero >> 24;
        if(hero_cat >= 0 && hero_cat <= 8) {
            out_stats[hero_cat]++;
        }

        if (score_hero > score_villain) wins++;
        else if (score_hero == score_villain) ties++;
    }

    *out_wins = wins;
    *out_ties = ties;
    *out_total = sims;
}