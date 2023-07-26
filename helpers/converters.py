from interactions import BaseContext, Converter


class LowerConverter(Converter):
    async def convert(self, ctx: BaseContext, argument: str):
        return argument.lower()
