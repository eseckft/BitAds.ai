# TODO List

### Ping task
- [ ] Make miner ping task async and move it to background instead of main process
- [ ] Make sure that validator ping task have to be in `forward` method

### API client
- [ ] Make BitAds client base class and implement sync (almost) and async version + mocked client
- [ ] Instead of `json()` in client use Pydantic models

### Dependency injection
- [ ] Make wallet info not global and pass it to necessary classes: APIClient, BaseStorage

### Implementation in variation
- [ ] Consider creating JsonStorage or SQLiteStorage implementation instead of FileStorage

### Global
- [ ] Update project to new BitTensor template version
- [ ] Unit tests