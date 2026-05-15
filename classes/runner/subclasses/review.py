




class ReviewRunner:
    def __init__(self, runner):
        self.runner = runner

    async def _update_review_cache(self):
        '''Обновляет кеш отзывов'''
        profile = await self.runner.account.profile.profile()
        self.runner.old_reviews = self.runner.reviews
        self.runner.reviews = profile.reviews

    async def _compare_review_cache(self):
        '''Сравнивает кеш отзывов'''
        result = []
        if self.runner.reviews != self.runner.old_reviews:
            for review in self.runner.reviews:
                if review not in self.runner.old_reviews:
                    result.append(review)
        return result